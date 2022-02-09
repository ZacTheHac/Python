from imageai.Prediction.Custom import CustomImagePrediction
import os

execution_path = "G:\\Python"


predictor = CustomImagePrediction()
predictor.setModelPath(model_path=os.path.join(execution_path, "ImageAI\\datasets\\Maned_wolves_are_not_foxes_even_babies\\models\\model_ex-029_acc-0.905797.h5"))
predictor.setJsonPath(model_json=os.path.join(execution_path, "ImageAI\\datasets\\Maned_wolves_are_not_foxes_even_babies\\json\\model_class.json"))
predictor.loadFullModel(num_objects=3)

print("\n\n\n")

ImagePath=os.path.join(execution_path, "ImageAI\\Testing images")
pictures=os.listdir(ImagePath)
for pic in pictures:
    results, probabilities = predictor.predictImage(image_input=os.path.join(ImagePath, pic), result_count=3)
    print(pic)
    for res in results[:-1]:
        print(res,end=" ")
        print("|",end=" ")
    print(results[len(results)-1])

    i=0
    while i<len(results):
        length = len(results[i])
        print(str(probabilities[i])[:length],end = "%  ") #this only works if we have names like 3 characters or longer, but I don't expect many names shorter than that
        i+=1
    print()
    #print(results)
    #print(probabilities)
    print("------------------------------------------------------------")
    print()

#results, probabilities = predictor.predictImage(image_input=os.path.join(execution_path, "ImageAI\\Maney_face.jpg"), result_count=3)