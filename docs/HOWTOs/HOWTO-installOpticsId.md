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

1. First, you need to make sure that everything is up-to-date on your computer. In this version of the program, we are using a python interpreter 3.9 or 3.8, pycharm version 2021.1.3 (community edition), and BigSur (version 11.4) on macOS (click on the apple in the top-left corner of your screen, and then "about this Mac") or Windows 10 on a PC.

2. Clone the repository. With the link for [Optics-ID](https://github.com/PyMarc2/Optics-ID/tree/benjustine-microraman), you will find a green "Code" button at the top-right corner of the page. Click on it.

   ![github](https://github.com/PyMarc2/Optics-ID/blob/benjustine-microraman/docs/images/github.png)

   Then, click on the pad icon to copy the link. This will give you the url in case you want the dynamic code. You can also download the ZIP if you simply want the code at its current state, but the first option is preferred. 

   With the link, you can clone the repo on apps like gitkraken or GitHub Desktop.

   For your information, a repository is a the folder where our data/code is stored and can be updated.

3. Once you you have cloned your repository to your computer and have acces to the code, make sure to create and install a virtual environment (if needed, here is the [HOWTO-venv](https://github.com/DCC-Lab/Documentation/blob/master/HOWTO/HOWTO-PythonVirtualEnvironment(venv).md) made by DCC-Lab). Then, activate it. 

   1. Using the following line in your terminal should create the folder *venv*, but make sure you are in the right directory* first (in Optics-ID). 

      ```bash
      $ python3 -m venv venv
      ```

   ​	*You can use the commands "cd [directory]" and "ls" to navigate your documents and folders.

   2. Once the virtual environment is created, you can activate it by writing in your command prompt

      ```bash
      $ source venv/bin/activate
      ```

   3. You will know that you have been successful when you can read "(venv)" at the beginning of the command line.

      ![venv](https://github.com/PyMarc2/Optics-ID/blob/benjustine-microraman/docs/images/venv.png)

      This means that your venv exists and is activated.

4. Use the requirements.txt file given in the repository to install all necessary modules, with the command presented hereunder.

   ```bash
   $ pip install -r requirements.txt
   ```

   While handling the setup of modules, you may encounter errors. Here is the most commun one and basic steps to correct the situation:

   ------

   ```bash
   ERROR: Failed building wheel for seabreeze
   Failed to build seabreeze
   ERROR: Could not build wheels for seabreeze which use PEP 517 and cannot be installed directly
   ```

   1. Write the following command:

      ```bash
      $ sudo xcodebuild -licence
      ```

      You have to agree to the xcode license in order for seabreeze to be installed. The command «sudo» needs to be run as an administrator, which means it will need your password. Once you have entered your password correctly, you can respond "agree" when asked, then press "enter" button, and then, you are good to go.

   2. To make sure everything has gone according to plan, simply re-enter the line used to install the requirements.

   ------

   One other essential python module is pyusb. However, since you probably created a brand new venv for the project, you will need to get the usb library as well, which can be tricky. Perhaps, the libusb is already downloaded on your computer, in which case you won't need to follow the next steps - directly skip to the last step - in order for your app to work perfectly. Otherwise, here are a few additional steps for you to read carefully. You will also need to install git. If you are not sure wheter or not you have libusb, homebrew or git installed, you can consider that they are in fact not on your computer and follow the next steps accordingly.

   ------

   ### For macOS - M1 chip

   1. Go to your home directory by using the "cd" command once and without any arguments.

   2. Run the following command on your terminal:

      ```bash
      $ touch .zshrc
      ```

   3. Open and modify the hidden file with the following code:

      ```bash
      $ nano ~/.zshrc
      ```

      You have now accessed the file and can edit it as you please.

   4. Add the following line on the file:

      ```txt
      export PATH=/opt/homebrew/bin:$PATH
      ```

   5. Last but not least, run the file to make the new path available:

      ```bash
      $ source ~/.zshrc
      ```

   6. From there, follow the steps described for a macOS - Intel chip.

   ------

   ### For macOS - Intel chip

   1. Before downloading libusb, you will need [Homebrew](https://brew.sh/), a package manager complementary to pip. To install, simply write in your terminal, in any directory:

      ```bash
      $ /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
      ```

   2. Then, install git.**

      ```bash
      $ brew install git
      ```

   3. You can now deactivate your virtual environment simply by writing "deactivate" directly in your terminal, no matter where you may have ended up in your directories. 

   4. Now that you are back in your local directories, install libusb with the following line of code:

      ```bash
      $ brew install libusb
      ```

   5. Link libusb to the abovementionned module.

      ```bash
      $ brew link libusb
      ```

      This step can be asked for "by the terminal" itself. Thus, I would invite you to read carefully every error or warning message that could occur when downloading anything in Terminal. It is also possible that everything went well, therfore rendering this step futile. An additional step I used afterwards was:

      ```bash
      $ brew link --overwrite libusb
      ```

   ------

   ### For windows

   Use the option that applies to you, then follow 4 easy steps.

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

5. Now that Homebrew, libusb and every module cited in requirements.txt has been acquired, your work is done. All you have to do now is activate the virtual environment, run the opt-id file and admire your beautiful results!

You can now proceed with your research and let our app marvel you, as well as awaken your curiosity.

![GUI](https://github.com/PyMarc2/Optics-ID/blob/benjustine-microraman/docs/images/raman12.png)

------

** Even if you already have git installed on your computer, you will need it in your homebrew in order for libusb to work and connect with the pyusb module.

