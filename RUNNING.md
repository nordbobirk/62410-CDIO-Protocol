# Running the robot and controller
To run the robot and controller, both must be on the same network (not "DTU secure", which has firewall rules blocking SSH traffic). Then, SSH in to the robot with the credentials `robot:maker`. Then, `cd` into the `robot` dir and run the robot with `python3 robot.py` (consider pulling changes first with `git pull`). Now, the robot is running.
In the controller, create or edit the file `controller.config` and write
```
EV3_HOST=<ev3-ip>
EV3_PORT=9999
```
where `<ev3-ip>` is the IP of the EV3. Now you can run the controller with `python3 controller.py`. By default, it will run in autonomous mode. To run in interactive mode, meaning the robot only does anything when told to do so, give the `--it` flag when running the controller. In interactive mode, you give commands in the controller terminal for the robot. To run the robot with the GUI for debugging, run with the `--gui` flag. To run with logging enabled, run with the `--log` flag.
## Interactive mode
When running the controller in interactive mode with the `--it` flag, you can specify commands using their [protocol](https://github.com/nordbobirk/62410-CDIO-Protocol) names (for instance `fwd` for forward). If no arguments are specified, the default arguments are used. If you want to override the default arguments, specify arguments using `key=value` separated for spaces, for instance `fwd seconds=1 lspeed=100 rspeed=100`.
