# distrobuilder-menu
* A console frontend to [Distrobuilder](https://linuxcontainers.org/distrobuilder/docs/latest/) for building standard or customised LXD / LXC images

---

<p align="center"><img src="https://github.com/itoffshore/distrobuilder-menu/assets/1141947/0eb19702-96f0-4436-a701-d69f863de9b9 /></p>

![Default Menu](https://github.com/itoffshore/distrobuilder-menu/assets/1141947/0eb19702-96f0-4436-a701-d69f863de9b9)
              
### :arrow_right: Features
* Download / update the latest [Distrobuilder templates](https://github.com/lxc/lxc-ci/tree/main/images)
* Create:
   - [cloud-init](https://cloudinit.readthedocs.io) `per-once` configuration
   - **template overrides** to include custom files / scripts
   - **custom templates** by **merging** the template override / cloud-init `yaml`
* Automatic selective caching of `json` output from LXD `images:`
  
   - read speed improved from `2mb` / `0.65` seconds **===>** `28kb` / `0.0083` seconds
    
* Auto generated menus for the available container flavours / versions your `platform` can build:

<p align="center"><img src="https://github.com/itoffshore/distrobuilder-menu/assets/1141947/52e0dd86-b894-4d79-b85c-73b2709440af" /></p>

* Optionally `import` the built LXD image into [`incus`](https://github.com/lxc/incus) or [`lxd`](https://ubuntu.com/lxd)

---  

### :arrow_right: Dependencies
* `pyyaml` / `urllib3`
* [Golang version of `yq`](https://github.com/mikefarah/yq)
* `lxc` client from [`incus`](https://github.com/lxc/incus) or [`lxd`](https://ubuntu.com/lxd)
* `distrobuilder-git` on **Arch Linux** (or Distrobuilder version `2.1.r255.g4ebc3cb` or higher)

---

### :arrow_right: Installation
* Isolated app: `pipx install https://github.com/itoffshore/distrobuilder-menu.git` (approx `4mb`)
* System module: `pip install https://github.com/itoffshore/distrobuilder-menu.git` (approx `900kb`)
* Under `lxd` run `ln -s /var/lib/lxd /var/lib/incus` (so the `unix.socket` is found by Distrobuilder)

