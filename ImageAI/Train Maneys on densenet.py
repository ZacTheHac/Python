from imageai.Prediction.Custom import ModelTraining
import os

trainer = ModelTraining()
trainer.setModelTypeAsDenseNet()
trainer.setDataDirectory("ImageAI\\datasets\\Maned_wolves_are_not_foxes")
trainer.trainModel(num_objects=4, num_experiments=5, enhance8_data=True, batch_size=32, show_network_summary=False,transfer_from_model="ImageAI\\DenseNet-BC-121-32.h5", initial_num_objects=1024,save_full_model=True)