import sys

NECESSARY_PACKAGES: dict[str, str] = {
    "pip": "23.1.2"
}


def get_requirements(*, filename: str) -> list[str]:
    """
    Read requirements file line by line and create a list of requirements.

    :param filename: Requirements file path
    :return: List of required packages
    """

    try:
        with open(filename, 'r') as file:
            requirements: list[str] = file.read().splitlines()

    except FileNotFoundError:
        print(f"File Not Found Error: No such file {filename}")
        sys.exit(2)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(2)

    else:
        if not requirements:
            return requirements

        requirements = list(filter(
            lambda requirement: not (not requirement or requirement.isspace()),
            requirements))
        return requirements


def clear_version(requirements: list[str]) -> None:
    """
    Clear version for each requirement in list with ONLY THIS format:
    {req_name}=={req_version}

    :param requirements: Requirements list
    """

    if not requirements:
        return

    for index, requirement in enumerate(requirements):
        req_name, *_ = requirement.partition('==')
        requirements[index] = req_name


def str_reqs(filename: str, reqs: list[str]) -> None:
    print(f"File {filename}:", *reqs, sep='\n', end='\n\n')


def check_duplicates(*args: list[str]) -> None:
    for arg in args:
        if len(set(arg)) != len(arg):
            print("Find duplicate packages!")
            sys.exit(2)
    return


def get_data(file_path: str, template_path: str) -> tuple[set[str], set[str]]:
    global NECESSARY_PACKAGES

    template_reqs: list[str] = get_requirements(filename=template_path)
    template_reqs.extend(NECESSARY_PACKAGES.keys())
    str_reqs(template_path, reqs=template_reqs)

    current_reqs: list[str] = get_requirements(filename=file_path)
    clear_version(requirements=current_reqs)
    str_reqs(file_path, reqs=current_reqs)

    check_duplicates(template_reqs, current_reqs)
    return set(template_reqs), set(current_reqs)


def check(*, file_path: str, template_path: str) -> None:
    template_reqs, current_reqs = get_data(file_path=file_path, template_path=template_path)

    diff = list(template_reqs ^ current_reqs)

    if not diff:
        print("Correct requirements found!")
        sys.exit(0)

    print(f"Conflicting requirements found: {len(diff)}")
    for req in diff:
        if req in template_reqs:
            print(f"Package `{req}` is not in the requirements list!")
        if req in current_reqs:
            print(f"There is no point in the `{req}` package!")
    sys.exit(2)


if __name__ == "__main__":
    check(file_path=sys.argv[1], template_path=sys.argv[2])
