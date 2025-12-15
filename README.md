# 🎉 Sponsors

## 🛴 Scooter Tools - App
[![Banner - Scooter Tools App](https://github.com/62fixolab/juanillo62gm/raw/master/assets/banner-scooter-tools.png)](https://scootertools.app)

## 📊 AdMate - App
[![Banner - AdMate App](https://github.com/62fixolab/juanillo62gm/raw/master/assets/banner-admate.png)](https://scootertools.app)

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

[![Project Maintenance][maintenance-shield]][maintainer]
[![BuyMeCoffee][buymecoffeebadge]][buymecoffee]

# Panda PWR

> [!IMPORTANT]
> This repository is currently not available in HACS. It is awaiting review by the HACS team to be included as a default repository. You can check the status of the review [here](https://github.com/hacs/default/pull/2851)

## Home Assistant Integration

Integrate your [Panda PWR from BIGTREETECH (BTT) | BIQU][pandapwrwiki] with Home Assistant.

[![PandaPWRDevice](/assets/panda_pwr_hardware.jpeg)][pandapwrwiki]

**This integration will set up the following platforms.**

| Platform        | Entity                  | Description                                       |
| --------------- | ----------------------- | ------------------------------------------------- |
| `switch`        | `PowerSwitch`           | Controls the power state of the PandaPWR device.  |
| `switch`        | `UsbSwitch`             | Controls the USB state of the PandaPWR device.    |
| `sensor`        | `CountdownStateSensor`  | Shows the countdown state of the device.          |
| `sensor`        | `AutoPoweroffSensor`    | Displays the auto power-off state.                |
| `sensor`        | `CountdownSensor`       | Shows the countdown timer in seconds.             |
| `sensor`        | `VoltageSensor`         | Measures the voltage (in volts).                  |
| `sensor`        | `CurrentSensor`         | Measures the current (in amperes).                |
| `sensor`        | `PowerSensor`           | Measures the power consumption (in watts).        |
| `sensor`        | `EnergyUsageSensor`     | Tracks energy usage (in kilowatt-hours).          |
| `binary_sensor` | `PowerStateBinarySensor`| Indicates if the power is on or off.              |
| `binary_sensor` | `UsbStateBinarySensor`  | Indicates if the USB port is on or off.           |
| `button`        | `Reset Energy Usage`    | Resets the energy usage statistics.               |
| `button`        | `Factory Reset`         | Performs a factory reset on the device.           |

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

<!---->

## Assets available [here](https://github.com/home-assistant/brands/tree/master/custom_integrations/panda_pwr)

## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

***

[pandapwrwiki]: https://bttwiki.com/Panda%20PWR.html
[buymecoffee]: https://paypal.me/juanillo62gm
[buymecoffeebadge]: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=for-the-badge
[commits-shield]: https://img.shields.io/github/commit-activity/y/juanillo62gm/HA-Panda-PWR.svg?style=for-the-badge
[commits]: https://github.com/62fixolab/HA-Panda-PWR/commits/main
[license-shield]: https://img.shields.io/github/license/juanillo62gm/HA-Panda-PWR.svg?style=for-the-badge
[maintainer]: https://github.com/62fixolab
[maintenance-shield]: https://img.shields.io/badge/maintainer-%20%40juanillo62gm-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/juanillo62gm/HA-Panda-PWR.svg?style=for-the-badge
[releases]: https://github.com/62fixolab/HA-Panda-PWR/releases
