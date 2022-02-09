from imageai.Prediction import ImagePrediction
import os

execution_path = os.getcwd()

prediction = ImagePrediction()
#prediction.setModelTypeAsResNet()
prediction.setModelTypeAsDenseNet()
#prediction.setModelPath(os.path.join(execution_path, "resnet50_weights_tf_dim_ordering_tf_kernels.h5"))
prediction.setModelPath(os.path.join(execution_path, "ImageAI\\DenseNet-BC-121-32.h5"))
prediction.loadModel()

predictions, probabilities = prediction.predictImage(os.path.join(execution_path, "ImageAI\\1.jpg"), result_count=15 )
for eachPrediction, eachProbability in zip(predictions, probabilities):
    print(eachPrediction , " : " , eachProbability)