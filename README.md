# DIY_battery_cycler
DIY battery cycler along with the python code and electrical schematic

I am working in the field of electrochemistry, being specific, on batteries. Battery testing devices are expensive, and add tremendous cost to the research. I am basically a chemical engineer with no formal training/education in electronics. I went through a few research articles published on making a DIY battery cycler and decided to make my own with a combination of a few not so informative schematics I found in the papers. I am making it open source for someone who is working on batteries, and doesnt have enough funding to get a commercial battery cycler. 

I am planning to add comprehensive description of its working and use. For now, anyone with a basic knowledge of ADC, DAC and opamps can understand the schematic. With some basic knowledge of python, one can understand the different chage-discharge scripts given in All-F.py file. the Script.py file is to be run on a raspberry pi which is connected to the battery cycler circuit as shown in the schematic. Script.py calls the required functions from All_F.py. These both files need to be in the same folder. 

Don't forget to install python libraries for MCP4725 and ADS1115 for raspberry pi. 

It will take some time to create a comprehensive guide. Feel free to contact me meanwhle in the case of any help.
