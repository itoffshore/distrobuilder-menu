# distrobuilder-menu
* A console frontend to [Distrobuilder](https://linuxcontainers.org/distrobuilder/docs/latest/) for building standard or customised LXD / LXC images

---

![Default Menu](https://github.com/itoffshore/distrobuilder-menu/assets/1141947/0eb19702-96f0-4436-a701-d69f863de9b9)

### :arrow_right: Features
* Download / update the latest [Distrobuilder templates](https://github.com/lxc/lxc-ci/tree/main/images)
* Create **template overrides** to include custom files / scripts
* Create [cloud-init](https://cloudinit.readthedocs.io) configuration
* Generate a custom template by merging the template override / cloud-init `yaml`
* Automatic selective caching of `json` output from LXD `images:`
  
   - from `2mb` / `0.65` seconds **===>** `28kb` / `0.0083` seconds
    
* Auto generated menus for the available container flavours / versions your `platform` can build

### :arrow_right: Dependencies
* [Golang version of `yq`](https://github.com/mikefarah/yq)
* `lxc` client from [`incus`](https://github.com/lxc/incus) or [`lxd`](https://ubuntu.com/lxd)
* `pyyaml` / `urllib3`

### :arrow_right: Installation
* Isolated app: `pipx install https://github.com/itoffshore/distrobuilder-menu.git` (approx `4mb`)
* System module: `pip install https://github.com/itoffshore/distrobuilder-menu.git` (approx `900kb`)

