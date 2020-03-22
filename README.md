# matrixlock

![i3lock-matrix Demo](demo.gif)

The script [matrixlock.py](matrixlock.py) in this repository lets you use the
Matrix as i3's lock screen.

## Requirements

The script currently has the requirements below. You should not find it too
difficult to edit [matrixlock.py](matrixlock.py) to use a slightly different
stack, such as a different terminal. If you do do that, please submit a Pull
Request to share your work with others.

 * Python 3.7+
 * Bash
 * Compton
 * xfce4-terminal
 * [cmatrix](https://github.com/abishekvashok/cmatrix)

## Set up

Make sure you have all of the above requirements.

Add the following to your Compton config:

    opacity-rule = ["10:name = 'i3lock'"]

(If you want more / less transparency of the circle while typing, change `10`).

I do this by having the above line in a file `compton.conf` and in my i3 config:

    exec --no-startup-id compton --config ~/.config/i3/compton.conf

Download [matrixlock.py](matrixlock.py) and make it executable:

    chmod +x matrixlock.py

Then, you should already be able to do:

    ./matrixlock.py

To automatically lock the screen after 5 minutes, add the following to your
i3 config:

    exec --no-startup-id xautolock -time 5 -locker ~/.config/i3/matrixlock.py

(Install `xautolock` if you don't have it.)

I furthermore use the following power menu:

```
set $Locker ~/.config/i3/matrixlock.py 1 & sleep 1

set $mode_system System (l) lock, (e) logout, (s) suspend, (h) hibernate, (r) reboot, (Shift+s) shutdown
mode "$mode_system" {
    bindsym l exec --no-startup-id $Locker, mode "default"
    bindsym e exec --no-startup-id i3-msg exit, mode "default"
    bindsym s exec --no-startup-id $Locker && systemctl suspend, mode "default"
    bindsym h exec --no-startup-id $Locker && systemctl hibernate, mode "default"
    bindsym r exec --no-startup-id systemctl reboot, mode "default"
    bindsym Shift+s exec --no-startup-id systemctl poweroff -i, mode "default"  

    # back to normal: Enter or Escape
    bindsym Return mode "default"
    bindsym Escape mode "default"
}

bindsym $mod+Pause mode "$mode_system"
bindsym --release XF86PowerOff mode "$mode_system"
```

Note `matrixlock` in the first line and that it only uses a single ampersand.
The last two lines let me invoke the power menu when I press
<kbd>Mod</kbd>+<kbd>Pause</kbd> or the Power button on my laptop.

## Acknowledgements

This script would not have been possible without
[this Youtube video](https://www.youtube.com/watch?v=jDyQHt2Iiro).
