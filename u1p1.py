NLP = { 
    "domain name" : "Natural Language Processing (NLP)",
    "Description" : "Teaches computers to understand human languageProcesses text and spoken wordsCaptures context, intent, and sentimentBridges communication between humans and machines",
    "Two real -world application" : "Apple's Siri,Sentiment Analysis",
    "popular python libraries" : "NLTK,spaCy"
}

speech_processing = { 
    "domain name" : "Audio AI",
    "Description" : " Speech processing is a field of artificial intelligence and signal processing covering Speech Recognition, Librosa, and Whisper.",
    "Two real -world application" : "Apple Siri or Google Assistant",
    "popular python libraries" : "SpeechRecognition,OpenAI Whisper"
}

Computer_Vision = { 
    "domain name" : "Computer Vision",
    "Description" : "Computer Vision enables machines and software to derive meaningful information from visual inputs—such as digital images, video streams, and 3D sensor data—and take automated action or make decisions based on that data.",
    "Two real -world application" : "Self-driving cars,X-rays, MRIs, and CT scans ",
    "popular python libraries" : "OpenCV"
}

Robotics = { 
    "domain name" : "Intelligent Systems",
    "Description" : " Robotics is an interdisciplinary field combining engineering and computer science to design, build, and operate programmable machines. Key details include Robotics, Autonomous Navigation, and Computer Vision.",
    "Two real -world application" : "Automated Manufacturing,Autonomous Delivery Drones & Vehicles",
    "popular python libraries" : "SROSPy,OpenCV"
}


print("1 - NLP")
print("2 - Speech Processing")
print("3 - Computer Vision")
print("4 - Robotics")

user = int(input("Enter Topic Number : "))

match user:
    case 1 :
        print(NLP)
    case 2 : 
        print(speech_processing)
    case 3 :
        print(Computer_Vision)
    case 4 : 
        print(Robotics)