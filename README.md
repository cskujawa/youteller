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
        <li><a href="#about-me">About Me</a></li>
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
<img src=https://github.com/cskujawa/youteller/blob/main/docs/images/Youteller_Transactions.png alt="App Example">

### :warning: :warning: :warning: Disclaimer :warning: :warning: :warning:
This documentation and the project as a whole are a work in progress.

To say this project at this stage is based on and not just a slightly modified version of Firefly III would be an understatement.
Huge thanks to https://github.com/JC5 for making a fantastic application.
https://github.com/firefly-iii/firefly-iii

This docker-compose project is the foundation for creating a more sophisticated financial wellness system for myself.
I am only sharing this in the hopes that it can serve as a reference for others trying to do the same thing.

<p align="right">(<a href="#top">back to top</a>)</p>

### Built With

Firefly III serves as the frontend for this stack. I've modified it in just a few places to allow myself to sync using a button from within the Firefly III transactions page (as seen in the screenshot).
* Added an additional route to the existing web router https://github.com/cskujawa/youteller/blob/main/firefly/html/routes/web.php#L1237
* Added an additional controller to handle API requests to the youteller-api service https://github.com/cskujawa/youteller/blob/main/firefly/html/app/Http/Controllers/Transaction/SyncController.php
* Added a button to handle sending the request from the UI https://github.com/cskujawa/youteller/blob/main/firefly/html/resources/views/transactions/index.twig#L82

The youteller-api python backend implements the Plaid python package for syncing financial information. It also handles translating the data to a format Firefly III can handle, synchronizing initial balances, and API calls to Firefly III to import all available transactions.

* [![Laravel][Laravel.com]][Laravel-url]
* [![MariaDB][Mariadb.org]][Mariadb-url]
* [![Python][Python.org]][Python-url]

<p align="right">(<a href="#top">back to top</a>)</p>

### About Me

Hi, I'm Cole. I'm not a full time developer and I like it that way. If you have questions about how I implemented this or are seeking advice about a similar project or implementation of this feel free to reach out, though I may not respond quickly.

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- GETTING STARTED -->
## Getting Started

### Pre-Requisites
1. Docker-compose
2. Docker
3. Plaid Developer Account, Client ID, and Secret https://dashboard.plaid.com/account/keys
4. Plaid IDs and Access Tokens for each account you plan on syncing

### Starting the project
1. Clone project
2. Open the Portfolio.py file, this is where you will link your .env variables to an account object in the Portfolio
3. Copy the /youteller-api/.env.example file to /youteller-api/.env and fill in the relevant details
4. Copy the /.env.example to /.env and fill in the relevant details
5. Copy the /.db.env.example to /.db.env and fill in the relevant details
6. Check the ports in the /docker-compose.yaml and the /youteller-api/Dockerfile and ensure they are available and the ones you want to use
7. Ensure you are in the root /youteller/ directory, if not, get there
8. Run `docker compose up -d app db`
9. That will start the Firefly web app, if you didn't change the port for Firefly it will be at http://serverip:83
10. Setup your Firefly accounts (this app currently expects them to all be asset accounts, even credit cards)
11. Update the list of accounts in Portfolio.py
12. Update the information in /youteller-api/.env
13. Run `docker compose up -d youteller-api`

If you need to stop the project it's `docker compose stop`
If you want to reset the Plaid cursor positions just delete the files in /youteller-api/cursors

This is a standalone environment that runs on Docker Compose. None of the containerized apps require any dependencies to be pre-installed or exist on the host OS. That all being said, if you have Docker Compose you should be able to clone or fork this repo, change to the project directory update the .env files (.env, .db.env, /youteller-api/.env), update the Portfolio.py variables, and boot it.

This stack was built with the intention of it not being accessible from the web, so accordingly the ports are mapped to local only ports on my bare metal server.

The Plaid integration is not a full fledged integration, there is no method for connecting to Plaid to auth or acquire any IDs or Access Codes.
To get the access codes required for the integration to work you will need to either have a full fledged Plaid integration or use something like the Plaid quick start to get the access codes for the accounts you want to access.
For more information about which configuration options you will need to provide and requirements review the .env.example file for the youteller-api
https://github.com/cskujawa/youteller/blob/main/youteller-api/.env.example

This stack is not intended to work with every possible bank supported by Plaid, it has only been tested for my personal banks.

Prior to booting up the youteller-api container you should ensure your Firefly III instance is up and running, and you will need to create the accounts you want connected to Plaid as well as an API token for Firefly III. 
For more information about which configuration options you will need to provide and requirements review the .env.example file for the youteller-api
https://github.com/cskujawa/youteller/blob/main/youteller-api/.env.example

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
