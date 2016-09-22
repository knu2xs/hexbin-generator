# import modules
import winreg


def get_child_keys(key_path):
    """
    Get the full path of first generation child keys under the parent key listed.
    :param key_path: Path to the parent key in registry.
    :return: List of the full path to child keys.
    """
    # open the parent key
    parent_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path)

    # variables to track progress and store results
    error = False
    counter = 0
    key_list = []

    # while everything is going good
    while not error:

        try:
            # get the child key in the iterated position
            child_key = winreg.EnumKey(parent_key, counter)

            # add the located key to the list
            key_list.append('{}\\{}'.format(key_path, child_key))

            # increment the counter
            counter += 1

        # when something blows up...typically because no key is found
        except Exception as e:

            # switch the error flag to true, stopping the iteration
            error = True

    # give the accumulated list back
    return key_list


def get_first_child_key(key_path, pattern):
    """
    Based on the pattern provided, find the key with a matching string in it.
    :param key_path: Full string path to the key.
    :param pattern: Pattern to be located.
    :return: Full path of the first key path matching the provided pattern.
    """
    # get a list of paths to keys under the parent key path provided
    key_list = get_child_keys(key_path)

    # iterate the list of key paths
    for key in key_list:

        # if the key matches the pattern
        if key.find(pattern):

            # pass back the provided key path
            return key


def get_current_business_analyst_usa_data_key():
    """
    Get the key for the current data installation of Business Analyst data.
    :return: Key for the current data installation of Business Analyst data.
    """
    return get_first_child_key('Software\ESRI\BusinessAnalyst\Datasets', 'USA_ESRI')


def get_business_analyst_key_value(locator_key):
    """
    In the Business Analyst key, get the value corresponding to the provied locator key.
    :param locator_key: Locator key.
    :return: Key value.
    """
    # open the key to the current installation of Business Analyst data
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, get_current_business_analyst_usa_data_key())

    # query the value of the locator key
    return winreg.QueryValueEx(key, locator_key)[0]


def get_usa_locator_path():
    """
    Get the directory path to the address locator installed with Business Analyst USA data.
    :return: String directory path to the address locator installed with Business Analyst USA data.
    """
    return get_business_analyst_key_value('Locator')


def get_usa_network_dataset_path():
    """
    Get the directory path to the network dataset installed with Business Analyst USA data.
    :return: String directory path to the network dataset installed with Business Analyst USA data.
    """
    return get_business_analyst_key_value('StreetsNetwork')


def get_usa_data_path():
    """
    Get the directory path where the Business Analyst USA data is located.
    :return: String directory path to where the Business Analyst USA data is installed.
    """
    return get_business_analyst_key_value('DataInstallDir')
