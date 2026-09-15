# Projects & data

DreamLake organizes assets in a hierarchy: a **project** contains
**episodes**, episodes contain **files**. **Bindrs** group episodes, and
**datasets** group bindrs.

## Projects

```bash file="terminal"
dreamlake create project my-robots --description "robot captures"   # private
dreamlake create project shared-set --public                        # public
dreamlake update project my-robots --public                         # flip visibility
dreamlake list project
dreamlake delete project my-robots                                  # hard-delete the whole subtree
```

Projects are **private by default**; `--public` / `--visibility public`
shares them. `update project` also changes `--name`, `--description`, `--tags`.

> **Warning:** `delete project` / `delete episode` / `delete file` permanently remove the
> node and its subtree (including the underlying storage objects). The CLI
> prompts for confirmation unless you pass `--yes`.

## Bindrs

A **bindr** groups episodes (matched by a glob over their node path).

```bash file="terminal"
dreamlake create bindr front-cam --project my-robots --episode "camera/front/*"
dreamlake update bindr front-cam --project my-robots --add "2026/04/*"
dreamlake update bindr front-cam --project my-robots --remove "run-bad"
dreamlake list bindr --project my-robots
dreamlake delete bindr front-cam --project my-robots
```

## Datasets

A **dataset** groups bindrs (matched by a glob over their name).

```bash file="terminal"
dreamlake create dataset train-v1 --project my-robots --tags robotics,training
dreamlake update dataset train-v1 --project my-robots --add "front-*"
dreamlake list dataset --project my-robots
dreamlake delete dataset train-v1 --project my-robots
```

## Episodes & files

```bash file="terminal"
dreamlake list episode --project my-robots
dreamlake delete episode run-001 --project my-robots                 # hard-delete episode + its files
dreamlake delete file /camera/front/clip.mp4 --episode my-robots:run-001
```

`delete file` also accepts a folder path to remove a whole subtree.
