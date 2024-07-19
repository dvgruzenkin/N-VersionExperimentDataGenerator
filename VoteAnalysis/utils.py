from typing import Tuple, Union


def input_num(user_str: str = 'Please enter number', limit: Tuple[float, float] = (float('-inf'), float('inf')),
              target_type: type = int, included_borders: bool = False, round_to: int = 6) -> Union[int, float]:
    """
    Prompt the user to enter a number within specified limits and convert it to the target type.

    :param user_str: Prompt message for the user.
    :param limit: Tuple representing the inclusive limits for the number.
    :param target_type: Type to which the input should be converted, default is int.
    :param included_borders: Flag indicating whether the borders are included in the limit.
    :param round_to: Number of decimal places to round to.
    :return: The user input converted to the target type and rounded.
    """
    incorrect_val = True
    while incorrect_val:
        try:
            user_num = target_type(input(user_str))
            if (limit[0] >= user_num >= limit[1] and not included_borders) or \
                    (limit[0] > user_num > limit[1] and included_borders):
                raise ValueError(f'Expected value from {limit[0]} to {limit[1]}')
        except ValueError as err:
            print(f'Entered value is incorrect! {err}')
            incorrect_val = True
        except Exception as err:
            print(f'Unknown error! {err}')
            incorrect_val = True
        else:
            user_num = round(user_num, round_to)
            incorrect_val = False
    return user_num

def check_is_none(var, err_str='Variable is None') -> bool:
    """
    Checks the value of the variable for None and sends error message.

    :return: Boolean response to belonging to None.
    """
    if var is None:
        print(err_str)
        return False
    return True