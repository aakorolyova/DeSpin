# DeSpin
A prototype system for detecting spin (distorted reporting of research results) in biomedical publications

This folder contains script files and models for DeSpin (Detector of Spin) prototype system.

To set up the prototype, you need to do the following:
1) Download the files from DeSpin directory and subdirectories to the folder where you want to install the system (let's suppose it is called DeSpinDir).
2) Download the models archives from the models folder:
https://mycore.core-cloud.net/index.php/s/PS1Dno4iaBn6JlK
Unpack them into the models subfolder in yor folder with scripts (DeSpinDir/models). The structure of the folders should be as follows:
DeSpinDir/models/<task_name>, where task_name is one of the following: out_sig_rel, po, rep, sentence_classification, similarity.
3) Download BioBERT pre-trained model weigths (https://github.com/naver/biobert-pretrained/releases). We used v1.0-pubmed-pmc - Pre-trained weight of BioBERT v1.0 (+PubMed 200K +PMC 270K).
4) Download SciBERT pre-trained model weigths for tensorflow (https://github.com/allenai/scibert), scibert-scivocab-uncased model.
5) In the file DeSpinDir/ak_pc_config.cfg, specify the paths for BioBERT and SciBERT models, in the variables BioBERT_model and SciBERT_model, respectively.
6) The following dependencies are needed to run the system: \\
nltk3.4
numpy1.16.4
pandas0.24.1
pickle
sklearn0.20.3
spacy2.0.18
tensorflow1.13.1
tkinter
unicodedata
urllib

7) Open the interface by running the command ' python3 \_\_init\_\_.py ' in DeSpinDir. You can now load a text in the .txt format(File - Import Text Only) and use annotation and information extraction functions of the interface. Use the Algorithms menu to choose information extraction functions; choose the Annotations menu to visualize and manage annotations.
