# Gain Tips

If you experience issues with corrupt / missing data, you might be using the wrong gain value for your receiver.

Depending on where you live and how close you are to a P2000 tower, the signal might be too strong or too weak to decode properly.

By using a program like <a href="https://airspy.com/" target="_blank">AirSpy</a> you can visualize your incoming signal and debug accordingly.

Click on the gear icon on the top-left to open the settings menu and start playing with the gain slider.

Here is an example of a **good** gain value. (0 dB)
We only receive a spike around 169.65Mhz (169.645Mhz is close enough) and can easily distinguish the signal from the background noise.
<img src="/assets/screenshots/goodgain.png">

Here is an example of **too high** of a gain. (46.9 dB)
Here the SDR becomes overloaded by the incoming signal.
The main frequency we are looking for clips out of the viewable window and multimple harmonics suddenly appear in places they should not be.
<img src="/assets/screenshots/badgain.png">

Tweak your gain value using, for example, AirSpy untill you are satisfied with the looks of the spectrum.
Take note of the number at the top-right of the gain-slider and use it in your **Open112** configuration.
