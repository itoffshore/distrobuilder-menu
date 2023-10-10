# distrobuilder-menu
* A [python](https://www.python.org/) console frontend to [Distrobuilder](https://linuxcontainers.org/distrobuilder/docs/latest/) for building standard or **customised LXD / LXC** images

---

![Default Menu](https://github.com/itoffshore/distrobuilder-menu/assets/1141947/0eb19702-96f0-4436-a701-d69f863de9b9)

---
              
### :arrow_right: Features
* Download / update the latest [Distrobuilder templates](https://github.com/lxc/lxc-ci/tree/main/images) via the Github REST API
* Create:
   - [cloud-init](https://cloudinit.readthedocs.io) `per-once` / standard configuration
   - **template overrides** to include custom files / scripts
   - **custom templates** by **merging** the template override / cloud-init `yaml`
* Automatic selective caching of `json` output from LXD `images:`
  
   - Read speed improved from `1mb` / `0.65` seconds **===>** `30kb` / `0.0083` seconds
   - Fast menu generation (typically `0.03` seconds or less)
   - Auto generated menus for the available container flavours / versions your `platform` can build:

<p align="center"><img src="https://github.com/itoffshore/distrobuilder-menu/assets/1141947/52e0dd86-b894-4d79-b85c-73b2709440af" /></p>

* Optionally `import` the built LXD image into [`incus`](https://github.com/lxc/incus) or [`lxd`](https://ubuntu.com/lxd)

--- 
### :arrow_right: Command line options:
```
usage: dbmenu [-h] [--lxd | --lxc | -o | -g | -i | -c | -e | -d | -m | -y | -u] [-s] [-t]
              [--rate] [--reset]

Menu driven LXD / LXC images for Distrobuilder

options:
  -h, --help      show this help message and exit
  --lxd           build LXD container / vm image (default)
  --lxc           build LXC container image
  -o, --override  create new template override
  -g, --generate  generate custom template from override
  -i, --init      create / edit cloud-init configuration
  -c, --copy      copy existing template / override
  -e, --edit      edit existing template / override
  -d, --delete    delete template / override
  -m, --move      move / rename template or override
  -y, --merge     merge cloudinit configuration with yq
  -u, --update    force update templates (default auto weekly)
  -s, --show      show configuration settings
  -t, --timer     debug timer used in testing
  --rate          show current Github API Rate Limit
  --reset         reset dbmenu base directory configuration
```
### :arrow_right: User Configuration:
* User configuration is stored under `~/.config/dbmenu.yaml` & is auto generated with sensible defaults on the first run of `dbmenu`
* The path to the **distrobuilder** area can be optionally changed from the **default** `~/distrobuilder` on first run or at any time via the `dbmenu --reset` command line option
```
[~]$ cat ~/.config/dbmenu.yaml
config_dir: /home/stuart/.config
main_dir: /home/stuart/devops/distrobuilder
target_dir: /home/stuart/devops/distrobuilder/build
files_dir: /home/stuart/devops/distrobuilder/files
template_dir: /home/stuart/devops/distrobuilder/templates
cloudinit_dir: /home/stuart/devops/distrobuilder/cloudinit
dbmenu_config: /home/stuart/.config/dbmenu.yaml
gh_owner: lxc
gh_repo: lxc-ci
gh_api_url: https://api.github.com
github_token: ''
cache_dir: false
cleanup: true
compression: xz
console_editor: nano
debug: false
disable_overlay: false
import_into_lxd: true
json_cachefile: /home/stuart/devops/distrobuilder/templates/cache.json
lxd_json: /home/stuart/devops/distrobuilder/templates/lxd.json
lxd_output_type: unified
subdir_custom: /home/stuart/devops/distrobuilder/templates/custom
subdir_images: /home/stuart/devops/distrobuilder/templates/images
subdir_overrides: /home/stuart/devops/distrobuilder/templates/overrides
cloudinit_network_dir: /home/stuart/devops/distrobuilder/cloudinit/network-data
cloudinit_user_dir: /home/stuart/devops/distrobuilder/cloudinit/user-data
cloudinit_vendor_dir: /home/stuart/devops/distrobuilder/cloudinit/vendor-data
timeout: false
yq_check: true
```
* For normal operation it's **not** necessary to add a Github Personal Access Token
* Unauthenticated Github API limits are not normally exceeded due to `connection-pooling` in `urllib3`  
---

### :arrow_right: Dependencies
* `pyyaml` / `urllib3`
* [Golang version of `yq`](https://github.com/mikefarah/yq)
* `lxc` client from [`incus`](https://github.com/lxc/incus) or [`lxd`](https://ubuntu.com/lxd)
* `distrobuilder-git` on **Arch Linux** (or Distrobuilder version `2.1.r255.g4ebc3cb` or higher)

---

### :arrow_right: Installation
* ✅ Isolated app:

   - `pipx install https://github.com/itoffshore/distrobuilder-menu.git`
   - size on disk `4mb`

* ‼️ System module:
  
   - `pip install https://github.com/itoffshore/distrobuilder-menu.git`
   - size on disk `900kb`

* ⚠️ Under `lxd` ensure [Distrobuilder](https://linuxcontainers.org/distrobuilder/docs/latest/) can find `unix.socket`
  
   - `ln -s /var/lib/lxd /var/lib/incus`
 
---

### ❓ Creating Images

`dbmenu` was inspired by & follows a similar methodology to [Hashicorp Packer](https://www.packer.io/) which builds / creates templates in layers:

* Create a **_base_** image override for your chosen distribution with your `shell` / package customizations that overrides a **standard template**
* Create a **_specific_** override / `cloud-init` config for your custom **service container** that contains things **not** in your **_base_** image template (e.g **web services** / **database**)
* Generate a **Custom Template** which uses your custom **_base_** image template as the `SOURCE` template & **merges** your _specific_ overrides / cloud-init

---

### 📰 Template Examples
* This repo's `examples` directory is also packaged under `site-packages` - e.g for `pipx` installs:

   - `~/.local/pipx/venvs/distrobuilder-menu/lib/python3.11/site-packages/examples`
    
* These `examples` show how to create images for:
  
   - Alpine Linux / Ubuntu **_base_** images
   - [Alpine Linux](https://alpinelinux.org/) build environment containing the `alpine-sdk` & [most of the steps](https://wiki.alpinelinux.org/wiki/Creating_an_Alpine_package#Setup_your_system_and_account) for packaging / contributing to Alpine
   - Ubuntu Gitlab container that installs Gitlab on first `boot` via `cloud-init`
 
---
   
### 🏗️ Creating / Building a Custom Template

* Empty input for each menu option / choice should `return` you to the **Main Menu** (`main event loop`)

* **_Create Custom Override_**
* Optionally - **_Create cloud-init Config_**
* **_Generate Custom Template_**

   - this option gives choices to **merge** a **Custom Override** & **cloud-init** configuration
   - you could also just **_Merge cloud-init Config_** into an existing template if you only need that option
    
* **_Build image_** - choosing the template type:

   - **LXD images** are built by `default`
   - to build `lxc` images start the app with `dbmenu --lxc` 
   - **_default container_** (LXC & LXD)
   - **_cloud container_** (LXC & LXD)
   - **_vm_** (LXD only)   
