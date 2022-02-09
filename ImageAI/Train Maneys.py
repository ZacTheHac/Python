from imageai.Prediction.Custom import ModelTraining

model_trainer = ModelTraining()
model_trainer.setModelTypeAsDenseNet()
model_trainer.setDataDirectory("ImageAI\\datasets\\Maned_wolves_are_not_foxes_even_babies")
model_trainer.trainModel(num_objects=3, num_experiments=30, enhance_data=True, batch_size=18, show_network_summary=False,save_full_model=True,continue_from_model="ImageAI\\datasets\\Maned_wolves_are_not_foxes_even_babies\\models\\model_ex-029_acc-0.905797.h5")