![Installations](https://img.shields.io/badge/dynamic/json?color=41BDF5&logo=home-assistant&label=Installations&suffix=%20installs&cacheSeconds=15600&style=for-the-badge&url=https://analytics.home-assistant.io/custom_integrations.json&query=$.panda_pwr.total)
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

[![Project Maintenance][maintenance-shield]][maintainer]
[![BuyMeCoffee][buymecoffeebadge]][buymecoffee]

# 🎉 Sponsors

## Printer Tools App
[![Banner - Printer Tools App](https://github.com/62fixolab/62fixolab/raw/master/assets/banner-printer-tools.png)](https://printertools.app)

## Scooter Tools App
[![Banner - Scooter Tools App](https://github.com/62fixolab/62fixolab/raw/master/assets/banner-scooter-tools.png)](https://scootertools.app)

## AdMate App
[![Banner - AdMate App](https://github.com/62fixolab/62fixolab/raw/master/assets/banner-admate.png)](https://admate.dev)

# Panda PWR

> [!IMPORTANT]
> This repository is currently not available in HACS. It is awaiting review by the HACS team to be included as a default repository. You can check the status of the review [here](https://github.com/hacs/default/pull/2851)

## Home Assistant Integration

Integrate your [Panda PWR from BIGTREETECH (BTT) | BIQU][pandapwrwiki] with Home Assistant.

[![PandaPWRDevice](/assets/panda_pwr_hardware.jpeg)][pandapwrwiki]

**This integration will set up the following platforms.**

| Platform        | Entity                    | Description                                                                 |
| --------------- | ------------------------- | --------------------------------------------------------------------------- |
| `switch`        | Power switch              | Turns the mains output on or off.                                           |
| `switch`        | USB switch                | Turns the USB output on or off.                                             |
| `switch`        | Shutdown timer            | Starts or stops the countdown that cuts the mains output when it ends.      |
| `switch`        | Auto power-off            | Firmware flag the countdown needs; follows Panda Touch when bound to one.   |
| `number`        | Countdown time            | Shutdown timer duration in seconds (up to 24 h); shows what is left while it runs. |
| `button`        | Pause shutdown timer      | Pauses a running shutdown timer.                                            |
| `button`        | Resume shutdown timer     | Resumes a paused shutdown timer.                                            |
| `button`        | Reset energy usage        | Resets the energy counter. **Disabled by default.**                        |
| `button`        | Factory reset             | Factory resets the device; it leaves your Wi-Fi. **Disabled by default.**   |
| `sensor`        | Voltage                   | Mains voltage (V).                                                          |
| `sensor`        | Current                   | Current drawn (A).                                                          |
| `sensor`        | Power                     | Power drawn (W).                                                            |
| `sensor`        | Energy usage              | Energy counter (kWh), ready for the Energy dashboard.                       |
| `sensor`        | Countdown                 | Seconds left on the shutdown timer.                                         |
| `sensor`        | Countdown state           | Stopped, running, paused or paused by Panda Touch.                          |
| `sensor`        | Auto power-off state      | Raw auto power-off flag (0 or 1).                                           |
| `binary_sensor` | Power state               | Whether the mains output is on.                                             |
| `binary_sensor` | USB state                 | Whether the USB output is on.                                               |

The integration polls the device once every 30 seconds and shares that reading with every entity.
When the Panda PWR is unreachable, its entities show as unavailable instead of reporting zero.

> [!TIP]
> The two destructive buttons are disabled by default. Enable them from the entity settings if you need them.

## **Installation**

### **Option 1: Installation via HACS**

1. Open Home Assistant and navigate to **Settings** → **Devices & Services** → **HACS**.

2. Click on the three dots in the top-right corner of the HACS page and select **Custom Repositories**.

3. Add the repository URL to the **Custom Repository** field:
    ```
    https://github.com/62fixolab/HA-Panda-PWR
    ```

4. Select **Integration** as the repository type and click **Add**.

5. Once the repository is added, find the integration in HACS, click **Install**, and follow the installation prompts.

6. Restart Home Assistant after completing the installation.

7. In the Home Assistant UI, navigate to **Configuration** → **Integrations**, click the "+" button, and search for **Panda PWR**.

---

### **Option 2: Manual Installation**

1. Open your Home Assistant configuration directory using your preferred file management tool.
   This is the folder where the `configuration.yaml` file is located.

2. Check if the `custom_components` folder exists in your configuration directory.
   - If it doesn’t exist, create a new folder named `custom_components`.

3. Inside the `custom_components` folder, create a new folder called `panda_pwr`.

4. Download **all** the files from the `custom_components/panda_pwr/` folder in this repository.

5. Place the downloaded files into the `panda_pwr` folder you just created.

6. Restart Home Assistant to load the new integration.

7. In the Home Assistant UI, navigate to **Configuration** → **Integrations**, click the "+" button, and search for **Panda PWR**.

---

## Configuration is done in the UI

1. Reserve the Panda PWR's IP address in your router so it does not change.
2. Add the **Panda PWR** integration and enter that IP address.

If the IP address changes anyway, open the integration, choose **Reconfigure** and enter the new one.
Entities and their history are kept. Adding the same device again at its new address also updates it.

## Diagnostics

From the device page, **Download diagnostics** saves the latest reading and firmware details to attach to an issue.
IP addresses, the device's access point name and its password are removed from the file.

## Assets available [here](https://github.com/home-assistant/brands/tree/master/custom_integrations/panda_pwr)

## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

***

[pandapwrwiki]: https://bttwiki.com/Panda%20PWR.html
[buymecoffee]: https://paypal.me/juanillo62gm
[buymecoffeebadge]: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=for-the-badge
[commits-shield]: https://img.shields.io/github/commit-activity/y/62fixolab/HA-Panda-PWR.svg?style=for-the-badge
[commits]: https://github.com/62fixolab/HA-Panda-PWR/commits/main
[license-shield]: https://img.shields.io/github/license/62fixolab/HA-Panda-PWR.svg?style=for-the-badge
[maintainer]: https://github.com/62fixolab
[maintenance-shield]: https://img.shields.io/badge/maintainer-%20%40juanillo62gm-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/62fixolab/HA-Panda-PWR.svg?style=for-the-badge
[releases]: https://github.com/62fixolab/HA-Panda-PWR/releases
