# **How to Install the Optics-Id App on any computer**

------

This tutorial should help you to install correctly the Optics-Id app, but more specificaly the microRamanView window. The first window, or filterView window, shall work on its own when the aforementioned installation is done.

## What is the Optics-Id app?

------

The Optics-Id app is your new best friend! It is designed to control simultaneously a stage, spectrometer and a light source of any kind. Its main purpose is to scan a sample of your choice and render an hyperspectral image of said sample. The user interface is quite intuitive, and will give you access to saved spectra, matrices, background information, a preview of the data, and much more.

## How to use the UI?

------

Once the program is rightfully installed, you can access [HOWTO-OpticsId](https://github.com/PyMarc2/Optics-ID) for more information on fonctionnalities and special features of the app.

## How to install Optics-Id on your computer?

------

1. First, you need to make sure that everything is up-to-date on your computer. In this version of the program, we are using a python interpreter 3.9 or 3.8, pycharm version 2021.1.3 (community edition), and BigSur (version 11.4) on macOS (click on the apple in the top-left corner of your screen, and then "about this Mac") or Windows 10 on a PC;

2. Once you have acces to the code and you have cloned your repository to your computer, make sure to create and install a virtual environment with the requirements given in the repository (if needed, here is the [HOWTO-venv](https://github.com/DCC-Lab/Documentation/blob/master/HOWTO/HOWTO-PythonVirtualEnvironment(venv).md) made by DCC-Lab). Then, activate it;

3. One essential python module, installed in your virtual environment by the command presented hereunder, is pyusb.

   ```bash
   $ pip install -r requirements.txt
   ```

   However, since you probably created a brand new venv for the project, you will need to get the usb library as well, which can be tricky. Perhaps, the libusb is already downloaded on your computer, in which case you won't need to follow the next steps - directly skip to the step 4 - in order for your app to work perfectly. Otherwise, here are a few additional steps for you to read carefully. You will also need to install git.

   ------

   ### For macOS

   3.1 - Before downloading libusb, you will need [Homebrew](https://brew.sh/), a package manager complementary to pip. To install, simply write in your terminal (for macOS or Linux only):

   ```bash
   $ /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

   Please note that steps 3.1 and 3.2 are exectuted while the venv is activated.

   3.2** - Then, install git.

   ```bash
   $ brew install git
   ```

   3.3 - You can now deactivate your virtual environment simply by writing "deactivate" directly in your terminal, no matter where you may have ended up in your directories. 

   3.4 - Now that you are back in your local directories, install libusb with the following line of code:

   ```bash
   $ brew install libusb
   ```

   3.5 - Link libusb to the abovementionned module.

   ```bash
   $ brew link libusb
   ```

   This step can be asked for "by the terminal" itself. Thus, I would invite you to read carefully every error or warning message that could occur when downloading anything in Terminal. It is also possible that everything went well, therfore rendering this step futile. An additional step I used afterwards was:

   ```bash
   $ brew link --overwrite libusb
   ```

   ------

   ### For windows

   Use the option that applies to you between 1, 2 and 3, then follow 4 easy steps.

   1. Install libusb on a 64bits system and Python 64bits

      1. Go to https://libusb.info/ in the Downloads tab and click on Latest Windows Binaries

      2. Unzip the file, if you don't have 7zip go download it on https://www.7-zip.org/ (take the second download link)

      3. In this same directory, go in the most recent (here VS20XX\MS64\dll) and copy "libusb-1.0.dll" to paste it in C:\Windows\System32

      4. Go to the most recent VS20XXMS64 and copy "libusb-1.0.lib" to paste it in C:\UsersNameAppDataLocalProgramsPythonPython3X\libs

      *Small note* If you don't see AppData, just go to display and check the "Hidden items" option.

   2. Install libusb on a 64bits system and Python 32bits
      1. Go to https://libusb.info/ in the Downloads tab and click on Latest Windows Binaries
      2. Unzip the file in a directory, if you don't have 7zip go download it on https://www.7-zip.org/ (take the second download link)
      3. In this same directory, go in the most recent (here VS20XX\MS32\dll) and copy "libusb-1.0.dll" to paste it in C:\Windows\SysWOW64
      4. Go to the most recent VS20XX\MS32\dll and copy "libusb-1.0.lib" to paste it in C:\Users\NameAppDataLocalPrograms\Python\Python3X\libs

      *Small note* If you don't see AppData, just go to display and check the "Hidden items" option.

   3. Install libusb on a 32bits system and Python 32bits

      1. Go to https://libusb.info/ in the Downloads tab and click on Latest Windows Binaries

      2. Unzip the file in a directory, if you don't have 7zip go download it on https://www.7-zip.org/ (take the first download link)

      3. In this same directory, go in the most recent (here, VS20XX\MS32\dll) and copy "libusb-1.0.dll" to paste it in C:\Windows\System32

      4. Go to the most recent VS20XX\MS32\dll and copy "libusb-1.0.lib" to paste it in C:\Users\NameAppDataLocalPrograms\Python\Python3X\libs

      *Small note* If you don't see AppData, just go to display and check the "Hidden items" option.

   ------

4. Now that Homebrew, libusb and every module cited in requirements.txt has been acquired, your work is done. All you have to do now is activate the virtual environment, run the opt-id file and admire your beautiful results!

You can now proceed with your research and let our app marvel you, as well as awaken your curiosity.

![GUI](https://github.com/PyMarc2/Optics-ID/blob/benjustine-microraman/docs/images/raman12.png)

------

** Even if you already have git installed on your computer, you will need it in your homebrew in order for libusb to work and connect with the pyusb module.

