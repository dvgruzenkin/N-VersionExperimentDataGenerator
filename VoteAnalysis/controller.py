from data_generator import NModule
from VoteAlgorithm import VoteAlgorithm
from typing import List


class Controller:
  def __init__(self, modules_list: List[NModule] = None, current_module_index: int = None, vote_algorithms_list: List = None, experiments_names_list: List = None):
    """
    Controller class constructor

    :param modules_list: List of current modules.
    :param current_module_index: Idex of curretn choosen module.
    :param vote_algorithms_list: List of current vote algorithms.
    :param experiments_names_list: List of experiments' name.
    """
    self._modules_list = modules_list or []
    self._current_module_index = current_module_index
    self._vote_algorithms_list = vote_algorithms_list or []
    self._experiments_names_list = experiments_names_list or []

  @property
  def modules_list(self) -> List[NModule]:
    return self._modules_list
  
  @property
  def current_module_index(self) -> int:
    return self._current_module_index
  
  @property
  def vote_algorithms_list(self) -> List:
    return self._vote_algorithms_list
  
  @property
  def experiments_names_list(self) -> List:
    return self._experiments_names_list
  
  @modules_list.setter
  def modules_list(self, module_list):
    self._modules_list = module_list
  
  @current_module_index.setter
  def current_module_index(self, current_module_index):
    self._current_module_index = current_module_index
  
  @vote_algorithms_list.setter
  def vote_algorithms_list(self, vote_algorithms_list):
    self._vote_algorithms_list = vote_algorithms_list
  
  @experiments_names_list.setter
  def experiments_names_list(self, vote_algorithms_list):
    self._experiments_names_list = vote_algorithms_list

  def add_module(self, name: str, round_digits: int, min_val: int, max_val: int):
    self._modules_list.append(NModule(name, round_digits, min_val, max_val))

  def load_module(self):
    module = NModule()
    module.load_module()
    self._modules_list.append(module)

  def save_module(self):
    self._modules_list[self.current_module_index].save_module()

  def add_versions(self):
    self._modules_list[self.current_module_index].add_versions()

  def load_module_with_versions(self):
    if self.current_module_index is not None:
        self._modules_list[self.current_module_index].load_module_with_versions()
    else:
        mdl = NModule()
        mdl.load_module_with_versions()
        self._modules_list.append(mdl)

  def save_module_with_versions(self):
    self._modules_list[self.current_module_index].save_module_with_versions()

  def generate_experiment_data(self, exp_name: str, iterations: int) -> str:
    generate_data = self.modules_list[self.current_module_index].generate_experiment_data(iterations, exp_name)
    if generate_data is not None:
        self._experiments_names_list.append(exp_name)
        return 'Experiment data was generated successfully!'
    return 'Error occurred during experiment data generation.'
  
  def save_experiment_data(self):
    self._modules_list[self.current_module_index].save_experiment_data()

  def get_experiment_data_from_db(self):
    self._experiments_names_list = self._modules_list[self.current_module_index].get_experiments_names()

  def load_experiment_data(self, exp_name_index: int):
    self._modules_list[self.current_module_index].load_experiment_data(self.experiments_names_list[exp_name_index])

  def add_vote_algorithm(self, algorithm_name: str, function_name: str, module_name: str):
    self._vote_algorithms_list.append(VoteAlgorithm(algorithm_name, function_name, module_name))

  def load_vote_algorithms(self):
    self._vote_algorithms_list = VoteAlgorithm.load_algorithms()

  def save_vote_algorithms(self):
    for algorithm in self._vote_algorithms_list:
      algorithm.save_vote_algorithm()

  def run_vote_algorithms(self):
    for algorithm in self._vote_algorithms_list:
      algorithm.vote(self.modules_list[self.current_module_index].global_results_lst)
      algorithm.save_vote_results()