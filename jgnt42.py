import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import re as re

#Set the theme of plots
sns.set_theme(context='notebook', style='whitegrid', palette='husl', font='sans-serif', font_scale=1, color_codes=True, rc=None)

#Problem 1

#Read spreadsheet
dataFrame: pd.DataFrame = pd.read_excel("./amazon_laptop_2023.xlsx", sheet_name=None)["amazon laptop 2023"]
renameMap = {}

#===Create graph for nan% of pre-cleaned data===%
missing = 100 * (dataFrame.isna().sum() / len(dataFrame))
fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(ax=ax, x="column", y="missing", data=pd.DataFrame({'column': dataFrame.columns, 'missing': missing}))
plt.xticks(rotation = 45)
plt.xlabel("Column Name")
plt.ylabel("Percentage Missing")
plt.ylim(0,70)
plt.title("Percentage missing (Nan) of each column")
plt.savefig("nanPercentages.png", bbox_inches='tight')



#=== Clean Brand ===
brands = [
    ["HP", "^.*hp.*$"],
    ["Dell", "^.*(dell|latitude).*$"],
    ["Lenovo", "^.*lenovo.*$"],
    ["ASUS", "^.*asus.*$"],
    ["Acer", "^.*acer.*$"],
    ["Toughbook", "^.*toughbook.*$"],
    ["MSI", "^.*msi.*$"],
    ["Microsoft", "^.*microsoft.*$"],
    ["LG", "^.*lg.*$"],
    ["Gigabyte", "^.*gigabyte.*$"],
    ["Apple", "^.*(Apple|Mac).*$"],
    ["Alienware", "^.*alienware.*$"],
    ["ROKC", "^.*rokc.*$"],
    ["Samsung", "^.*samsung.*$"],
    ["Panasonic", "^.*panasonic.*$"]
          ]

#Format brand name
x = None
for pair in brands:
    y = dataFrame["brand"].str.match(pair[1], case=False, na=False)
    if type(x) == type(None):
        x = y
    else:
        x = x | y
    dataFrame.loc[y,"brand"] = pair[0]
dataFrame.loc[~x,"brand"] = "Unknown"



#=== clean model ===
#Drop null values
dataFrame.dropna(axis=0, subset="model", inplace=True)



#=== Clean screen_size ===
#Extract numerical values
dataFrame["screen_size"] = dataFrame["screen_size"].astype(str).str.extract('((\d+,)*\d+\.?\d*)')[0].astype(float)
renameMap["screen_size"] = "screen_size (inches)"
#Removal of nan
dataFrame.dropna(subset="screen_size", inplace=True)



#=== clean colour ===
patterns = [
    ["Gray", "(?:Gray|Grey|Gary|Graphite|Ash)"],
    ["Silver", "(?:Silver|Platinum|Alumin(i)?um|Lunar|Metallic|Mercury|Sliver)"],
    ["Black", "(?:Black|Dark Side|Balck|Midnight)"],
    ["Red", "(?:Red)"],
    ["White", "(?:White)"],
    ["Green", "(?:Green|Moss|Mint|Sage)"],
    ["Blue", "(?:Blue|Sky|Teal|Cobalt)"],
    ["Gold", "(?:Gold)"],
    ["Pink", "(?:Pink|Punk)"],
    ["Carbon Fiber", "(?:Carbon Fiber)"],
    ["Brown", "(?:Almond|Dune|Beige)"]
]

colours = ""

#Make naming of colours consistent. E.g. sky blue and pale blue will both be mapped to blue
for i in range(len(patterns)):
    pair = patterns[i]
    dataFrame.loc[dataFrame["color"].astype(str).str.contains(pair[1], regex=True, case=False), "color"] = pair[0]
    colours += pair[0]
    if (i < len(patterns)-1):
        colours += "|"
#Remove any extra colours and fill null values
dataFrame["color"] = np.where(dataFrame["color"].str.contains(colours, regex=True, case=False), dataFrame["color"], "Unknown")
dataFrame.fillna({"color":"Unknown"}, inplace=True)
renameMap["color"] = "colour"



#=== Clean harddisk ===
#Convert all to GB
x = dataFrame["harddisk"].astype(str).str.match('(.*TB.*)')
dataFrame["harddisk"] = dataFrame["harddisk"].astype(str).str.replace(',', '', regex=True).str.extract('((\d+,)*\d+\.?\d*)')[0].astype(float)
dataFrame["harddisk"] = np.where(x, dataFrame["harddisk"]*1000, dataFrame["harddisk"])
renameMap["harddisk"] = "harddisk (GB)"
dataFrame.dropna(subset="harddisk", inplace=True)



#=== Clean cpu===
patterns = [
    ["Intel Core i9", "Core ?i9"],
    ["Intel Core i7", "Core ?i7"],
    ["Intel Core i5", "Core ?i5"],
    ["Intel Core i3", "Core ?i3"],
    ["Intel Core Duo", "Intel Core Duo"],
    ["Intel 2 Core Duo", "Core 2 Duo"],
    ["Intel 2 Core Quad", "Core 2 Quad"],
    ["Intel Core M", "Core[ _]M"],
    ["Intel Mobile CPU", "Intel Mobile CPU"],
    ["Intel Celeron", "Celeron"],
    ["Intel Pentium", "Pentium"],
    ["Intel Atom", "Atom"],
    ["Intel Xeon", "Xeon"],
    ["AMD Ryzen 9", "Ryzen 9"],
    ["AMD Ryzen 7", "Ryzen 7"],
    ["AMD Ryzen 5", "Ryzen 5"],
    ["AMD Ryzen 3", "Ryzen 3"],
    ["AMD A Series", "(A[- ]?Series|7700K|AMD A4|A6-5200M)"],
    ["AMD R Series", "AMD R Series"],
    ["AMD Athlon", "Athlon"],
    ["Apple M1", "Apple M1"],
    ["Apple M2", "Apple M2"],
    ["Qualcomm Snapdragon", "Snapdragon"],
    ["ARM Cortex", "Cortex"],
    ["ARM 7100", "ARM 7100"],
    ["MediaTek MT8183", "MT8183"],
    ["MediaTek MT8127", "MT8127"],
    ["MediaTek Helip P60T", "MediaTek Helio P60T"],
    ["", "Unknown|68000|8032|Others"]
]

#Set cpu names to have same format
for i in range(len(patterns)):
    pair = patterns[i]
    dataFrame["cpu"] = np.where(dataFrame["cpu"].astype(str).str.contains(pair[1], regex=True, case=False), pair[0], dataFrame["cpu"])

#Drop nan values
dataFrame["cpu"].replace("^[/s]*$", np.nan, inplace=True, regex=True)
dataFrame.dropna(subset=["cpu"], inplace=True)



#=== Clean ram ===
#Convert all to GB
dataFrame["ram"] = dataFrame["ram"].astype(str).str.replace(',', '', regex=True).str.extract('((\d+,)*\d+\.?\d*)')[0].astype(float)
dataFrame["ram"] = np.round(np.where(dataFrame["ram"]>500, dataFrame["ram"]/1000, dataFrame["ram"]),1)
renameMap["ram"] = "ram (GB)"
dataFrame.dropna(subset="ram", inplace=True)



#=== Clean OS ===
patterns = [
    ["Windows", "Win"],
    ["MacOS", "Mac"],
    ["Chrome OS", "Chrome OS"],
    ["Linux", "Linux"]
]

#Make formatting of operating system consisten. E.g. 'Windows 11' and 'Windows Version 11' will both map to Windows
OSs = ""
for i in range(len(patterns)):
    pair = patterns[i]
    dataFrame["OS"] = np.where(dataFrame["OS"].astype(str).str.contains(pair[1], regex=True, case=False), pair[0], dataFrame["OS"])
    OSs += pair[0]
    if (i < len(patterns)-1):
        OSs += "|"

#Set null values to Windows if non-apple computer
x = dataFrame["OS"].str.contains(OSs, regex=True, case=False)
y = dataFrame["brand"].str.contains("Apple", regex=False, case=True)
dataFrame["OS"] = np.where(x&y, dataFrame["OS"], "Windows")
dataFrame["OS"] = np.where(x&y, "MacOS", dataFrame["OS"])



#=== Clean special_features ===
featureList = [["[^,]*Anti.{0,2}(Gla|refl)[^,]*", "Anti-Glare"],
              ["[^,]*Anti.{0,2}Smu[^,]*", "Anti-Smudge"],
              ["[^,]*Fingerprint[^,]*", "Fingerprint Reader"],
              ["[^,]*Stereo[^,]*", "Stereo Speakers"],
              ["[^,]*Gorilla Glass[^,]*", "Gorilla Glass"],
              ["[^,]*Back[^,]*Ke?y?B[^,]*", "Backlit Keyboard"],
              ["[^,]*(High Definition|HD)( Audio[^,]*)", "HD Audio"],
              ["[^,]*(Stylus|Pen)[^,]*", "Stylus"],
              ["[^,]*Spill[^,]*", "Spill Resistant"],
              ["[^,]*(Bezel|nanoedge)[^,]*", "Thin Bezel"],
              ["[^,]*Ghost[^,]*", "Anti-Ghost Key"],
              ["[^,]*Alexa[^,]*", "Alexa Built-in"],
              ["[^,]*(Lightweight|Portable)[^,]*", "Lightweight"],
              ["[^,]*Keypad[^,]*", "Numeric Keypad"],
              ["[^,]*Touch ?screen[^,]*", "Touchscreen"],
              ["[^,]*(Water|Washer)[^,]*", "Water Resistant"],
              ["[^,]*Memory Card[^,]*", "Memory Card Slot"],
              ["[^,]*Battery[^,]*", "Long Battery"],
              ["[^,]*Miracast[^,]*", "Miracast Technology"],
              ["[^,]*(GB RAM|Chiclet|Military|play on|Narrow|Information|Quality|Ergonomic|Dolby|Alcohol|Ruggedized|84 Key| i5|multitas|Killer|work|Multi|windows|camera|Intel|Infinity|Track|Premium|notebook|1.5|create|Full|entertain|refresh|stream)[^,]*,?", ""],

              ]
#Make special features have a consistent format
for pair in featureList:
    dataFrame["special_features"] = dataFrame["special_features"].str.replace(pat=pair[0],repl=pair[1],regex=True, case=False)
#Fill Nan values
dataFrame["special_features"].replace("^$", np.nan, inplace=True, regex=True)
renameMap["special_features"] = "features"



#=== clean graphics and graphics_coprocessor ===

#Get any GPUs in the graphics column and put in graphics column
dataFrame["graphics_coprocessor"].update(dataFrame["graphics"].replace(to_replace="^Integrated|Dedicated|shared$", value=np.nan, regex=True).dropna(axis=0))

#List of GPUs and what they should be mapped to
coprocessorList = [["^.*(Intel.*Iris|Iris Xe?|Intel Xe).*$", "Intel Iris Xe Graphics"],
                   ["^(AMD Radeon|.*(Radeon Graphics|AMD Integrated|Integrated AMD|Vega \d|Radeon R\d|Radeon 6\d0M).*)$", "AMD Integrated Graphics"],
                   ["^(Intel|.*(Intel( HD)? Integrated Graphics|Integrated Intel|Intel Graphics Integrated|UHD Graphics|Intel HD|HD (\d){3,4}|Intel 620U).*)$", "Intel Integrated Graphics"],
                   ["^(Integrated[ _]Graphics|inter?gr[ea]ted|HD Integrated Graphics)$", ""],
                   ["^.*[RG]TX.*4090(?![ -]?Ti).*$","Nvidia GeForce RTX 4090"],
                   ["^.*[RG]TX.*4080(?![ -]?Ti).*$","Nvidia GeForce RTX 4080"],
                   ["^.*[RG]TX.*4070(?![ -]?Ti).*$","Nvidia GeForce RTX 4070"],
                   ["^.*[RG]TX.*4060(?![ -]?Ti).*$","Nvidia GeForce RTX 4060"],
                   ["^.*[RG]TX.*4050(?![ -]?Ti).*$","Nvidia GeForce RTX 4050"],
                   ["^.*[RG]TX.*4000(?![ -]?Ti).*$","Nvidia GeForce RTX 4000"],
                   ["^.*RTX.*3080 ?Ti.*$","Nvidia GeForce RTX 3080-Ti"],
                   ["^.*[RG]TX.*3080(?![ -]Ti).*$$","Nvidia GeForce RTX 3080"],
                   ["^.*RTX.*3070 ?Ti.*$","Nvidia GeForce RTX 3070-Ti"],
                   ["^.*[RG]TX.*3070(?![ -]?Ti).*$","Nvidia GeForce RTX 3070"],
                   ["^.*[RG]TX.*3060(?![ -]?Ti).*$","Nvidia GeForce RTX 3060"],
                   ["^.*RTX.*3050 ?Ti.*$","Nvidia GeForce RTX 3050-Ti"],
                   ["^.*[RG]TX.*3050(?![ -]?Ti).*$","Nvidia GeForce RTX 3050"],
                   ["^.*[RG]TX.*3000(?![ -]?Ti).*$","Nvidia GeForce RTX 3000"],
                   ["^.*[RG]TX.*2080(?![ -]?Ti).*$","Nvidia GeForce RTX 2080"],
                   ["^.*[RG]TX.*2070(?![ -]?Ti).*$","Nvidia GeForce RTX 2070"],
                   ["^.*[RG]TX.*2060(?![ -]?Ti).*$","Nvidia GeForce RTX 2060"],
                   ["^.*[RG]TX.*2050(?![ -]?Ti).*$","Nvidia GeForce RTX 2050"],
                   ["^.*GTX.*1660 ?Ti.*$","Nvidia GeForce GTX 1660-Ti"],
                   ["^.*[RG]TX.*1660(?![ -]?Ti).*$","Nvidia GeForce GTX 1660"],
                   ["^.*GTX.*1650 ?Ti.*$","Nvidia GeForce GTX 1650-Ti"],
                   ["^.*[RG]TX.*1650(?![ -]?Ti).*$","Nvidia GeForce GTX 1650"],
                   ["^.*[RG]TX.*1070(?![ -]?Ti).*$","Nvidia GeForce GTX 1070"],
                   ["^.*[RG]TX.*1060(?![ -]?Ti).*$","Nvidia GeForce GTX 1060"],
                   ["^.*GTX.*1050 ?Ti.*$","Nvidia GeForce GTX 1050-Ti"],
                   ["^.*[RG]TX.*1050(?![ -]?Ti).*$","Nvidia GeForce GTX 1050"],
                   ["^.*GTX.*(965)(?![ -]?Ti).*$","Nvidia GeForce GTX 965M"],
                   ["^.*GeForce.*(940)(?![ -]?Ti).*$","Nvidia GeForce GTX 940MX"],
                   ["^.*GT.*(720)(?![ -]?Ti).*$","Nvidia GeForce GT 720M"],
                   ["^.*MX550.*$","Nvidia GeForce MX550"],
                   ["^.*MX450.*$","Nvidia GeForce MX450"],
                   ["^.*MX350.*$","Nvidia GeForce MX350"],
                   ["^.*MX250.*$","Nvidia GeForce MX250"],
                   ["^.*MX230.*$","Nvidia GeForce MX230"],
                   ["^.*MX150.*$","Nvidia GeForce MX150"],
                   ["^.*MX130.*$","Nvidia GeForce MX130"],
                   ["^.*T2000.*","Nvidia T2000"],
                   ["^.*T1200.*","Nvidia T1200"],
                   ["^.*T1000.*","Nvidia T1000"],
                   ["^.*T600.*","Nvidia T600"],
                   ["^.*T550.*","Nvidia T550"],
                   ["^.*T500.*","Nvidia T500"],
                   ["^.*A5500.*","Nvidia GeForce RTX A5500"],
                   ["^.*A4500.*","Nvidia GeForce RTX A4500"],
                   ["^.*A3000.*","Nvidia GeForce RTX A3000"],
                   ["^.*A2000.*","Nvidia GeForce RTX A2000"],
                   ["^.*A1000.*","Nvidia GeForce RTX A1000"],
                   ["^.*A500.*","Nvidia GeForce RTX A500"],
                   ["^.*3500 Ada.*","Nvidia GeForce RTX 3500 Ada"],
                   ["^.*2000 Ada.*","Nvidia GeForce RTX 2000 Ada"],
                   ["^.*Radeon 7 .*$","AMD Radeon 7 Graphics"],
                   ["^.*RX 7600.*$","AMD Radeon RX 7600"],
                   ["^.*RX 6800.*$","AMD Radeon RX 6800M"],
                   ["^.*Radeon Graphics 5500.*$", "AMD Radeon RX 5500"],
                   ["^.*Pro 560.*$","AMD Radeon Pro 560"],
                   ["^.*RX 540.*$","AMD Radeon RX 540"],
                   ["^.*Arc A370M.*","Intel Arc A370M"]
                   ]

#Ensure GPUs in graphics co_processor are formatted in the same way
pattern = "^("
for i in range(len(coprocessorList)):
    pair = coprocessorList[i]
    dataFrame["graphics_coprocessor"] = dataFrame["graphics_coprocessor"].str.replace(pat=pair[0], repl=pair[1], case=False, regex=True)
    if (i==len(coprocessorList)-1):
        pattern += pair[1] + ")$"
    else:
        pattern += pair[1] + "|"

#Remove remaining GPUs from graphics_coprocessor and fill in nans
dataFrame["graphics_coprocessor"] = np.where(dataFrame["graphics_coprocessor"].astype(str).str.match(pattern), dataFrame["graphics_coprocessor"], "Unknown")

#Update Graphics column to be only Integrated or Dedicated
dataFrame["graphics"] = np.where(dataFrame["graphics_coprocessor"].str.match("^.*(Nvidia|Radeon (RX|Pro|7 Graphics)|Intel Arc).*$", case = False), "Dedicated", "Integrated")
renameMap["graphics_coprocessor"] = "GPU"



#=== Clean cpu_speed ===
#Convert all to GHz
dataFrame.drop(axis=1, labels=["cpu_speed"], inplace=True)


#=== Clean price ===
#Extract numerical values
dataFrame["price"] = dataFrame["price"].astype(str).str.replace('[\$,]', '', regex=True).astype(float)
#Removal of nan
dataFrame["price"].replace(to_replace="^[/s]*$", value=np.nan, inplace=True, regex=True)
dataFrame.dropna(axis=0, inplace=True, subset=["price"])

renameMap["price"] = "price ($)"




#rename columns
dataFrame.rename(columns=renameMap, inplace=True)
#drop duplicated
dataFrame.drop_duplicates(inplace=True)


#save
dataFrame.to_excel("amazon_laptop_2023_cleaned.xlsx", index=False)






#Problem 2

#Filter out any laptops over 1500
dataFrame = dataFrame[dataFrame["price ($)"] <= 1500]

#Remove any duplicate laptops with almost identical prices 
df = dataFrame.copy()
df.loc[:,"price ($)"] = df["price ($)"].round(0)
dataFrame = dataFrame[~df.duplicated()]



#CUSTOMER 1
#Filter for Windows laptops with Ryzen and Nvidia GPUSs, Intel and Ryzen CPUs
gamingDF = dataFrame[(dataFrame["OS"] == "Windows") & dataFrame["GPU"].str.match("^.*[RG]TX? \d*(-Ti)?$", case=False, na=False) & dataFrame["cpu"].str.match("^.*(Core i\d|Ryzen \d).*$", case=False, na=False)]


#===Figure for GPU against Benchmark score===
#Find dataset at https://www.userbenchmark.com/resources/download/csv/GPU_UserBenchmarks.csv
gpuBenchmark = pd.read_csv("./GPU_UserBenchmarks.csv")
dic = {}
#Filter for only Nvidia GPU
gpuBenchmark = gpuBenchmark[gpuBenchmark["Brand"] == "Nvidia"]


#Find the GPU benchmarks for Nvidia cards in the coprocessorList
last1 = None
last2 = None
toFill = None
for gpu in coprocessorList:
    #Extracts part of GPU name which will match the imported dataset
    match = re.search("[RG]TX? \d+(-Ti|M)?$",gpu[1])
    if match == None:
        continue
    result = gpuBenchmark[gpuBenchmark["Model"].str.match("^.*" + match.group() + "$", case=False)]
    
    #Fill in missing value by looking at previous two existing values
    val = None
    if result.empty:
        if toFill != None:
            current = 2 * last1 - last2
            dic[toFill] = current
            last2 = last1
            last1 = current
        toFill = gpu[1]
        dic[toFill] = [match.group(), 0]
        continue
    
    current = result["Benchmark"].iloc[0]
    dic[gpu[1]] = [match.group(), current]

    #Fill in missing value by taking the mean of two values either side
    if toFill != None:
        if (current < last1):
            last2 = (last1 + current)/2
        else:
            last2 = 2 * last1 - last2
        dic[toFill][1] = last2
        toFill = None
    else:
        last2 = last1
    last1 = current

#Add series number for hue
for x in dic.values():
    series = int(re.search("\d+", x[0]).group()[0:2])
    if series > 50:
        series=int(series/10)*100
    x.append(str(series) + " Series")


#Make the graph
fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(ax = ax, x="GPU Model", y="Benchmark Score", hue="series", dodge=False, data=pd.DataFrame({"GPU Model":[x[0] for x in dic.values()], "Benchmark Score":[x[1] for x in dic.values()], "series":[x[2] for x in dic.values()]}))
plt.xticks(rotation = 45)
plt.title("Benchmark results of GPUs comapred to a RTX 2060S, ordered by series")
plt.ylim(0, 400)
plt.savefig("GPU_benchmark.png", bbox_inches='tight')
#Add GPU benchmark to the dataset
gamingDF["GPU_benchmark"] = [dic[x][1] for x in list(gamingDF["GPU"])]



#===Figure for average benchmark of CPU families===
#Find dataset at https://www.userbenchmark.com/resources/download/csv/CPU_UserBenchmarks.csv
cpuBenchmark = pd.read_csv("./CPU_UserBenchmarks.csv")

#Filter for Intel Core and Amd Ryzens
cpuBenchmark = cpuBenchmark[cpuBenchmark["Model"].str.match(".*(Core i\d|Ryzen \d).*")]
#Remove specific CPU models and only leave the family
cpuBenchmark["Model"] = cpuBenchmark["Model"].str.extract("(Core i\d|Ryzen \d)")[0]

#Make the graph
fig, ax = plt.subplots(figsize=(12, 6))

#Group by family
val = data=cpuBenchmark.loc[:,["Model","Benchmark"]].groupby("Model").mean()
sns.barplot(x=list(val.index), y=list(val["Benchmark"]))
plt.xticks(rotation = 45)
plt.title("Average benchmark of CPU families comapred to an Intel i9-9900K")
plt.xlabel("CPU Family")
plt.ylabel("CPU Benchmark")
plt.ylim(0, 100)
plt.savefig("CPU_family_benchmark.png", bbox_inches='tight')


#Store the CPU benchmark for each CPU
gamingDF["CPU_benchmark"] = [val.loc[re.search("(Core i\d|Ryzen \d)", x).group(), "Benchmark"] for x in list(gamingDF["cpu"])]
#Calculate gaming score
gamingDF["Gaming_Score"] = (gamingDF["ram (GB)"]*2) + (gamingDF["harddisk (GB)"]/20) + gamingDF["GPU_benchmark"] + gamingDF["CPU_benchmark"]
gamingDF["Gaming_Score_Efficiency"] = gamingDF["Gaming_Score"]/gamingDF["price ($)"]


#===Plot gaming Score===
fig, axes =plt.subplots(2,2, figsize=(12,12))
ax : plt.Axes = axes[0][0]
sns.scatterplot(ax = ax, x="price ($)", y="Gaming_Score", data=gamingDF)
ax.set_title("Gaming score against price ($)")
ax.set_xlabel("Price ($)")
ax.set_ylabel("Gaming Score")
ax.set_xlim(600, 1600)
ax.set_ylim(150, 400)


#===Plot Gaming Score Efficiency===
ax : plt.Axes = axes[0][1]
sns.scatterplot(ax = ax, x="price ($)", y="Gaming_Score_Efficiency", data=gamingDF)
ax.set_title("Gaming Efficiency against price ($)")
ax.set_xlabel("Price ($)")
ax.set_ylabel("Gaming Score Efficiency")
ax.set_xlim(600, 1600)
ax.set_ylim(0.1, 0.4)


#===Plot laptops with top 5 gaming scores===
ax : plt.Axes = axes[1,0]
df = gamingDF.nlargest(5, "Gaming_Score")
sns.barplot(ax = ax, x="model", y="Gaming_Score", data=df)
ax.set_title("5 laptops with the highest gaming score")
ax.bar_label(ax.containers[0], "$" + df["price ($)"].astype(str))
ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
ax.set_ylim(300, 400)
ax.set_xlabel("")
ax.set_ylabel("Gaming Score")


#===Plot laptops with top 5 gaming score efficiencies===
ax : plt.Axes = axes[1,1]
df = gamingDF.nlargest(5, "Gaming_Score_Efficiency")
sns.barplot(ax = ax, x="model", y="Gaming_Score_Efficiency", data=df)
ax.set_title("5 laptops with the highest gaming score efficiencies")
ax.bar_label(ax.containers[0], "$" + df["price ($)"].astype(str))
ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
ax.set_ylim(0.2, 0.4)
ax.set_xlabel("")
ax.set_ylabel("Gaming Score Efficiency")

#Save big figure
plt.savefig("gamingEfficiency_price.png", bbox_inches='tight')



#===Customer 2===
#Filter for below average screen size, above average rating and fingerprint readers
buisnessDf = dataFrame[(dataFrame["screen_size (inches)"] < dataFrame["screen_size (inches)"].mean()) &
                (dataFrame["rating"] > dataFrame["rating"].mean()) & (dataFrame["features"].str.contains("Fingerprint Reader"))]

#Plot screen size againt rating
fig, axes = plt.subplots(1,3, figsize=(12,6), gridspec_kw={'width_ratios': [2, 1, 1]})
ax = axes[0]
sns.scatterplot(ax=ax, data=dataFrame, x="screen_size (inches)", hue="screen_size (inches)", y="rating")
ax.legend([],[], frameon=False)
ax.set_title("Ratings of laptops compared to screensize")
ax.set_xlabel("Screen Size (Inches)")
ax.set_ylabel("Amazon User Rating")
ax.set_xlim(10,18)
ax.set_ylim(0,6)

#Boxplot for screen size
ax = axes[1]
sns.boxplot(ax=ax, data=dataFrame, y="screen_size (inches)")
ax.set_ylim(10,18)
ax.set_ylabel("")
ax.set_xlabel("Screen Size")

#Boxplot for rating
ax = axes[2]
sns.boxplot(ax=ax, data=dataFrame, y="rating")
ax.set_ylim(0,6)
ax.set_ylabel("")
ax.set_xlabel("Rating")

#Save big figure
plt.savefig("screenSize_Rating.png", bbox_inches='tight')



#Plot storage against price
fig, axes = plt.subplots(1,2, figsize=(12,6))

#Plot the top 5 laptops
ax : plt.Axes = axes[1]
df = buisnessDf.nlargest(5, "harddisk (GB)")
sns.barplot(ax = ax, x="model", y="harddisk (GB)", data=df)
ax.set_title("Price ($) of highest storage laptops")
ax.bar_label(ax.containers[0], "$" + df["price ($)"].astype(str))
ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
ax.set_xlabel("")
ax.set_ylabel("Storage space (GB)")


ax : plt.Axes = axes[0]
#Plot the log of harddisk
buisnessDf.loc[:,"harddisk (GB)"] = np.log2(buisnessDf["harddisk (GB)"])
sns.scatterplot(ax = ax, y="price ($)", x="harddisk (GB)", hue="rating", data=buisnessDf)
#Convert labels to be non-log
ticks = ax.get_xticklabels() 
for tick in ticks:
    tick.set_text(str(int(2**float(tick.get_text()))))
ax.set_xticklabels(ticks)
ax.set_ylim(400,1600)
ax.set_title("Storage against cost")
ax.set_ylabel("Price ($)")
ax.set_xlabel("Storage space (GB)")


plt.savefig("buisnessLaptops.png", bbox_inches='tight')
