# Simplicial complexes analysis in python

This is the python repository for the works:

- [Daniel Hernández Serrano, Juan Hernández-Serrano, Darío Sánchez Gómez, "Simplicial degree in complex networks. Applications of topological data analysis to network science", Chaos, Solitons & Fractals, Volume 137, 2020](https://www.sciencedirect.com/science/article/abs/pii/S0960077920302393)
- [Daniel Hernández Serrano, Javier Villarroel, Juan Hernández-Serrano, Ángel Tocino, "Stochastic simplicial contagion model", Chaos, Solitons & Fractals, Volume 167, 2023](https://www.sciencedirect.com/science/article/abs/pii/S0960077922011870)
- [Angel Tocino, Daniel Hernández Serrano, Juan Hernández-Serrano, Javier Villarroel, "A stochastic simplicial SIS model for complex networks", Communications in Nonlinear Science and Numerical Simulation, Volume 120, 2023](https://doi.org/10.1016/j.cnsns.2023.107161)
- *Angel Tocino, Daniel Hernández Serrano, Juan Hernández-Serrano, "A stochastic simplicial SIS model driven by two independent noises", under review in the Revista de la Unión Matemática Argentina*

## Setup

Copy `config.ini.template`, edit directory names, and optionally fill your PostgreSQL database details (required for parsing Scholp and ArXiv datasets).

Install all requirements in `requirements.txt`

## Structure

### Parsers

- `arxiv`: scripts for harvesting ArXiv datasets and loading simplicial complexes computed from them into the database
- `scholp`: scripts for loading simplicial complexes computed from downloaded Scholp datasets into the database.

### Working with simplicial complexes in the database (paper in [HHS20](https://www.sciencedirect.com/science/article/abs/pii/S0960077920302393))

- `facets.py`: script for computing facets. Run `python facets.py -h` for help.
- `faces_degrees`: compute q-faces and degrees. *It MUST be run after `facets.py`*. Run `python faces_degrees.py -h` for help.
- `export_faces_to_csv`: exports computed faces from the database to a CSV file. Run `python export_faces_to_csv.py -h` for help.
- `stats.py`: generate datasets and degrees statistics and exports them to a CSV file. Run `python stats.py -h` for help.
- `figures.py`: generates figures regarding datasets and degrees' statistics. *It MUST be run after `stats.py`*.

### The Stochastic Simplicial Contagion Model (paper in [HVHT23](https://www.sciencedirect.com/science/article/abs/pii/S0960077922011870))

- `HVHT23_contagion_experiments_by_region.json`: Defines experiment parameters for the contagion model simulations
- `HVHT23_simplagion_experiment_parameters.ipynb`: Outputs configuration setup (MUST be copied in `contagion_experiments.py`) for the contagion model based on the experiments defined in `HVHT23_contagion_experiments_by_region.json`
- `contagion_model.py`: Runs the stochastic simplicial contagion model on the datasets defined and using the parameters (experiments) defined in `contagion_experiments.py`. Run `python contagion_model.py -h` for help.

### A stochastic simplicial SIS model driven by two independent noises

- `THH25_simplagion_experiment_parameters.ipynb`: Outputs configuration setup (MUST be copied in `contagion_experiments.py`)
- `contagion_model.py`: Runs the stochastic simplicial contagion model on the datasets defined and using the parameters (experiments) defined in `contagion_experiments.py`. Run `python contagion_model.py -h` for help.
