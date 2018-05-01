# EnsambleTerrestre


Composición generativa basada en un modelo del movimiento de la tierra.



Requiere python >2.6, con opencv 2.4, RPI.GPIO y smbus.

	*pip install RPi.GPIO
	*sudo apt-get install -y python-smbus
	*sudo apt-get install -y i2c-tools

Habilitar puerto I2C desde raspi-config

	*sudo raspi-config

Configurar autorun como https://www.raspberrypi.org/forums/viewtopic.php?t=138861

---

Las direcciones de los dispositivos para la comunicación por I2C son
	* address_NE = 0x6A
	* address_SW = 0x3A