class Challenge:
    """A class representing a Project Euler challenge.

    This class contains all of the relevant properties to be able to create a README for a Project Euler challenge
    locally within this git repo.
    """

    def __init__(
        self,
        number: int,
        url: str,
        title: str,
        description: str,
        remote_content: dict[str, str] | None,
    ) -> None:
        """__init__ Initializes an instance of the Challenge class.

        Args:
            number (int): The number of this challenge.
            url (str): The URL to the webpage for the challenge.
            title (str): The title of the challenge.
            description (str): The description text for the challenge
            remote_content (dict[str, str] | None): A dictionary containing the filenames and URLs for resources that need to be downloaded locally, or None if this is not applicable.
        """
        self.number = number
        self.url = url
        self.title = title
        self.description = description
        self.remote_content = remote_content

    def __eq__(self, value: object) -> bool:
        """__eq__ Checks if the given object is equal to this instance.

        Args:
            value (object): The object to compare this instance to.

        Returns:
            bool: True if the objects are equal, false otherwise.
        """

        # Check if the object is an instance of the Challenge class, or a subclass of Challenge.
        if not isinstance(value, Challenge):
            # A Challenge can only be equal to another Challenge or subclass.
            return False

        # Return true if every property value is the same, otherwise return false.
        return (
            self.number == value.number
            and self.url == value.url
            and self.title == value.title
            and self.description == value.description
            and self.remote_content == value.remote_content
        )
