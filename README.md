<!-- PROJECT LOGO -->
<br />
<div align="center">
Youteller - Plaid - Firefly III

  <p align="center">
    <a href="https://github.com/othneildrew/Best-README-Template/issues">Report Bug</a>
    ·
    <a href="https://github.com/othneildrew/Best-README-Template/issues">Request Feature</a>
  </p>
</div>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
    </li>
    <li>
      <a href="#contributing">Contributing</a>
    </li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->
## About The Project

### :warning: :warning: :warning: Disclaimer :warning: :warning: :warning:
This documentation and the project as a whole are a work in progress.

To say this project at this stage is based on and not just a slightly modified version of Firefly III would be an understatement.
Huge thanks to https://github.com/JC5 for making a fantastic application.
https://github.com/firefly-iii/firefly-iii

This docker-compose project is the foundation for creating a more sophisticated financial wellness system for myself.
I am only sharing this in the hopes that it can serve as a reference for others trying to do the same thing.

<p align="right">(<a href="#top">back to top</a>)</p>


### Built With

Firefly III serves as the frontend for this stack

A simple python API server acts as the backend for processing anything I don't want to offload on Firefly

The python backend also implements a connection with Plaid for syncing financial information.

* [![Laravel][Laravel.com]][Laravel-url]
* [![MariaDB][Mariadb.org]][Mariadb-url]
* [![Python][Python.org]][Python-url]

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- GETTING STARTED -->
## Getting Started

This is a standalone environment that runs on Docker Compose. None of the containerized apps require any dependencies to be pre-installed or exist on the host OS. That all being said, if you have Docker Compose you should be able to clone or fork this repo, change to the project directory update the .env files and boot it.

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->

[Laravel.com]: https://img.shields.io/badge/Laravel-FF2D20?style=for-the-badge&logo=laravel&logoColor=white
[Laravel-url]: https://laravel.com
[Mariadb.org]: https://img.shields.io/badge/MariaDB-003545?style=for-the-badge&logo=mariadb&logoColor=white
[Mariadb-url]: https://mariadb.org/
[Python.org]: https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54
[Python-url]: https://www.python.org/
