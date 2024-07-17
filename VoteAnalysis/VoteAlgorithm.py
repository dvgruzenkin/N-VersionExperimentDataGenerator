"""
Vote algorithm model to make a vote and save and load it

Program for simulation several N-versions work of one module to test vote algorithms.
Experiment is carried out in Denis V. Gruzenkin PhD thesis writing.
"""

import inspect
import json
import os

from data_base_connector import DBConnector
from data_generator import NResult
from module_importer import ModuleNotLoadedError, FunctionNotFoundInModuleError

__author__ = "Denis V. Gruzenkin"
__copyright__ = "Copyright 2021, Denis V. Gruzenkin"
__credits__ = ["Denis V. Gruzenkin"]
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Denis V. Gruzenkin"
__email__ = "gruzenkin.denis@good-look.su"
__status__ = "Production"


class VoteAlgorithm:
    _db_name = 'experiment.db'

    def __init__(self, name: str, vote_func_name: str, module_name: str, module_pkg: str = 'VoteAlgs', new_id=None):
        self.name = name
        self._id = new_id
        self._vote_result = []

        self._vote_module = self._load_module(module_pkg, module_name)
        self._vote_algorithm = self._load_function(vote_func_name)

    def _load_module(self, module_pkg: str, module_name: str):
        try:
            module_pkg = __import__(f'{module_pkg}.{module_name}')
            if hasattr(module_pkg, module_name):
                return getattr(module_pkg, module_name)
            raise ModuleNotFoundError(f'Python module was not found by path: {module_pkg}.{module_name}')
        except ModuleNotFoundError as e:
            err_str = f'Module VoteAlgorithms.{module_name} cannot be loaded. Error: {e.msg}'
            print(err_str)
            raise ModuleNotFoundError(err_str)
        except Exception as e:
            print(e)
            raise e

    def _load_function(self, vote_func_name: str):
        if hasattr(self._vote_module, vote_func_name):
            return getattr(self._vote_module, vote_func_name)
        err_str = f'There is no function {vote_func_name} in {self._module_name}'
        print(err_str)
        raise FunctionNotFoundInModuleError(err_str)

    @property
    def vote_algorithm(self):
        return self._vote_algorithm

    @vote_algorithm.setter
    def vote_algorithm(self, vote_func):
        self._vote_algorithm = vote_func

    @property
    def vote_results(self):
        return self._vote_result

    @property
    def module_name(self):
        return self._module_name

    @module_name.setter
    def module_name(self, new_path: str):
        if os.path.isfile(new_path):
            self._module_name = new_path
        else:
            raise ModuleNotFoundError(f'Cannot find module by path: {new_path}')

    def vote(self, nversions_results: list[list[NResult]]):
        self._vote_result = [{'data': iteration_result, 'res': self._vote_algorithm(iteration_result)}
                             for iteration_result in nversions_results]

    def save_vote_algorithm(self):
        cur_conn = DBConnector(self._db_name)
        if not cur_conn.table_exists('algorithm'):
            create_query = '''
                CREATE TABLE algorithm (
                    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                    name VARCHAR(127) NOT NULL,
                    src_code TEXT NULL,
                    module_name VARCHAR(255) NOT NULL,
                    func_name VARCHAR(127) NOT NULL,
                    module_pkg VARCHAR(255) NULL
                );
            '''
            cur_conn.execute_query(create_query, [], True, False)

        if self._id is None:
            insert_query = f"""
                INSERT INTO algorithm (name, src_code, module_name, func_name, module_pkg) VALUES (
                    '{self.name}', '{json.dumps(inspect.getsource(self._vote_module))}', 
                    '{self._module_name}', '{self._vote_func_name}', 'VoteAlgorithms'
                );
            """
            self._id = cur_conn.execute_query(insert_query, [], True)[0][0]
        else:
            update_query = f"""
                UPDATE algorithm SET 
                    name = '{self.name}', 
                    src_code = '{json.dumps(inspect.getsource(self._vote_algorithm))}', 
                    module_name = '{self._module_name}' 
                WHERE id = {self._id};
            """
            cur_conn.execute_query(update_query, [], True, False)

    def save_vote_results(self):
        cur_conn = DBConnector(self._db_name)
        if not cur_conn.table_exists('vote_result'):
            create_query = '''
                CREATE TABLE vote_result (
                    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                    algorithm_id INTEGER NOT NULL,
                    experiment_data_id INTEGER NOT NULL,
                    vote_answer REAL NULL,
                    UNIQUE(algorithm_id, experiment_data_id, vote_answer) ON CONFLICT REPLACE,
                    FOREIGN KEY (algorithm_id) REFERENCES algorithm(id),
                    FOREIGN KEY (experiment_data_id) REFERENCES experiment_data(id)
                );
            '''
            cur_conn.execute_query(create_query, [], True, False)

        if self._id is None:
            self.save_vote_algorithm()

        res_insert_lst = [(self._id, iteration_res.id, res['res']) 
                          for res in self._vote_result for iteration_res in res['data']]
        if res_insert_lst:
            insert_query = '''
                INSERT INTO vote_result (algorithm_id, experiment_data_id, vote_answer) VALUES(?,?,?);
            '''
            cur_conn.execute_query(insert_query, res_insert_lst, True, False)

            if input('Do you want to load rows from DB? y - Yes; any key - No: ').upper() == 'Y':
                for res in self._vote_result:
                    tmp_ids = [
                        int(select_res[0][0]) 
                        for iteration_res in res['data'] 
                        for select_res in cur_conn.execute_query(f"""
                            SELECT id FROM vote_result 
                            WHERE algorithm_id = {self._id} 
                            AND experiment_data_id = {iteration_res.id} 
                            AND vote_answer = {res['res']}
                        """)
                        if select_res
                    ]
                    res['ids'] = tmp_ids

    def load_vote_results(self):
        # TODO: Дописать этот метод!
        pass

    @classmethod
    def load_algorithms(cls) -> list:
        cur_conn = DBConnector(cls._db_name)
        algorithms_list = []

        if cur_conn.table_exists('algorithm'):
            select_query = 'SELECT id, name, func_name, module_name, src_code, module_pkg FROM algorithm ORDER BY id;'
            q_set = cur_conn.execute_query(select_query)

            if q_set:
                for mdl in q_set:
                    try:
                        m_id = int(mdl[0])
                        m_alg_name, m_func, m_name, m_code, m_pkg = mdl[1:6]

                        if not os.path.isfile(f'{m_pkg}/{m_name}.py'):
                            with open(f'{m_pkg}/{m_name}.py', 'w') as mod_file:
                                mod_file.write(json.loads(m_code))

                        algorithms_list.append(VoteAlgorithm(m_alg_name, m_func, m_name, m_pkg, m_id))
                    except ValueError:
                        print(f'Incorrect algorithm identifier - {mdl[0]}. Row is skipped.')
                    except (ModuleNotFoundError, ModuleNotLoadedError, FunctionNotFoundInModuleError) as e:
                        print(f'Error: {e}. Row is skipped.')
                    except Exception as e:
                        print(f'Error: {e}. Row is skipped.')
            else:
                print('There are no algorithms modules to load')
        else:
            raise LookupError(f'There is no "algorithm" table in {cls._db_name} database. Save some algorithm before loading.')

        return algorithms_list

    def __str__(self):
        return f'{self.name} ({self._vote_func_name}) in {self._module_name}'
