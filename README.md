# run-gha-on-slurm

The purpose of this project is to run GitHub Actions on prem via our Slurm cluster.

# Overview
1. The Allocator polls the GitHub API for queued jobs
2. Whenever a job is queued, it allocates an ephemeral action runner on the Slurm cluster
3. Once the job is complete, the runner and Slurm resources are de-allocated

### Basic diagram of the system
```mermaid
flowchart LR
    GitHubAPI[("GitHub API")]
    ActionsRunners[("Allocator")]
    Slurm[("Slurm Compute Resources")]

    ActionsRunners --> | Poll Queued Jobs | GitHubAPI 
    ActionsRunners -->| Allocate Actions Runner| Slurm 
```

## Enabling Docker Within CI Jobs

```mermaid
graph TD
    A[Docker Rootless Daemon] -->| Creates | B[Docker Rootless Socket]
    B -->| Creates | C[Custom Actions Runner Image]
    C -.->| Calls | B
    C --->| Mounts | B
    C -->| Creates | E[CI Helper Containers]
    E -.->| Calls | B
```

Since CI Docker commands will use the same filesystem, as they have the same Docker socket, you need to configure the working directory of your runners accordingly. 

## Speeding up our Actions Runner Image

After we were able to run the actions runner image in as Slurm job using [sbatch](https://slurm.schedmd.com/sbatch.html) and [custom script](https://github.com/WATonomous/run-gha-on-slurm/blob/main/allocate-ephemeral-runner-from-docker.sh) we ran into the issue of having to pull the docker image for every job. From the time the script allocated resources to the time the job began was ~ 2 minutes. When you are running 70+ jobs in a workflow, with some jobs depending on others, this time adds up fast. 

Unfortunately, caching the image is not an elegant solution because this would require mounting the filesystem directory to the Slurm job. This means we would need to have multiple directories if we wanted to support multiple concurrent runners. This would require creating a system to manage these directories and would introduce the potenital for starvation and dead locks. 

This led us to investegate a [Docker pull through cache](https://docs.docker.com/docker-hub/mirror/).


### References
1. [Docker Rootless](https://docs.docker.com/engine/security/rootless/)
2. [Custom Actions Runner Image](https://github.com/WATonomous/actions-runner-image)
3. [Apptainer](https://apptainer.org/docs/user/main/index.html)
4. [Stargz Snapshotter](https://github.com/containerd/stargz-snapshotter)
5. [CVMFS](https://cvmfs.readthedocs.io/en/stable/)
6. [CVMFS Stratum 0](https://github.com/WATonomous/cvmfs-ephemeral/)


# Issues
- If script needs to be restart and runners are being built, the script will allocate new runners once its back up 

# Potential issue:
- job1 requires label1, label2
- job2 requires label1
- runner1 is allocated with label1, label2
- runner1 runs job2
- runner2 is allocated with label1
- runner2 CANT RUN job1
Won't be an issue if we use one label (small, medium, large) per job

