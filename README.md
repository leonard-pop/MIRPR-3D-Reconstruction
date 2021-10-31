# Reconstruction 3D

## Description

In terapia radiologica a diverselor boli este nevoie de construirea unor masti de protectie a anumitor parti ale corpului (de ex. protejarea fetei).
Daca aceste masti respecta cat mai mult fizionomia unui pacient, ele se transforma in aliati siguri ai pacientului, 
dar si ai medicului in combaterea bolilor si cresterea gradului de securitate a organelor care nu trebuie iradiate.

Constructia unei masti se poate adapta specificului unui pacient, respectand trasaturile fetei.
In acest context se doreste dezvoltarea unei aplicatii care pe baza imaginii fetei unei persoane sa poata extrage caracteristicile faciale 
si sa frunizeze un model 3D a acestora.

## Objective

Dezvoltarea unei aplicatii care permite incarcarea unor imagini ale pacientilor, capabila sa genereze, pe baza acestora,
un model 3D al fetei si/sau partii superioare a corpului acestuia. Modelul generat va fi intr-un format printabil la o imprimanta 3D.

## Main flow

Proiectul consta intr-o aplicatie Android, in care utilizatorul va putea incarca poze, fie facandu-le direct cu camera telefonului,
fie din memorie interna sau din alte forme de stocare.

Dupa ce poza este incarcata, aceasta va fi procesata in urmatorii pasi:

- Extragere caracteristici (folosind MediaPipe pentru fata, TBD pentru partea de gat si partile laterale ale capului)
- Generare poligoane pe baza caracteristicilor extrase (care vor fi sub forma de puncte intr-un spatiu 3d)
- Generare mesh bazat pe modelul obtinut

Rezultatul va fi un fisier in format **.stl** , care va putea fi vizualizat local (folosind android AR Scene Viewer, daca dispozitivul permite), dar si exportat.

## Implementation details

TODO

## References

[https://google.github.io/mediapipe/solutions/face\_mesh.html](https://google.github.io/mediapipe/solutions/face_mesh.html)

[https://github.com/microsoft/Deep3DFaceReconstruction](https://github.com/microsoft/Deep3DFaceReconstruction)
