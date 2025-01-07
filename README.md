Outdated, needs update.

# phomemo_p12
Python script to print text on a Phomemo P12 label printer

# Acknowledgements
Based on [phomemo_d30](https://github.com/polskafan/phomemo_d30) by polskafan,
[phomemo-tools](https://github.com/vivier/phomemo-tools) by Laurent Vivier and
[phomemo_m02s](https://github.com/theacodes/phomemo_m02s) by theacodes.

# Checkout and install
```bash
pip3 install phomemo-p12-tools
```

# Setup
Connect to printer with rfcomm

```bash
sudo rfcomm connect 1 XX:XX:XX:XX:XX:XX
```

Or windows, connect to P12 by 'Bluetooth & device' menu.

# Usage

```bash
phomemo_render_label "Hello world!" | phomemo_print_p12 --port=[device]
```

Or windows,

```cmd
phomemo_render_label "Hello world!" > label.pbm
phomemo_print_p12 --port=[device] label.pbm
```
