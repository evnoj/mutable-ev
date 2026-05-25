This dir contains the `.wav` files of alternate firmwares. The actual alternate firmware work may be on a different branch. The format of the filenames is:

```
<module-name>_<fw-name>_<date>_<commit>.wav
```
- `<module-name>`: the name of the module the firmware is for, ex. `rings`
- `<fw-name>`: the name/description of the alternate firmware
- `<date>`: the date the wav was built
- `<commit>`: the commit that the wav was built from

ex. `rings_modal-structure-retune_2026-05-24_9251574.wav` is the "modal structure retune" firmware for Rings, built on 2026-05-24 from commit `9251574`
