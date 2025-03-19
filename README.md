# Swing Trade Tracker 🚀

## Description
Swing Trade Tracker is a powerful and easy-to-use trade tracking system for traders who want to stay on top of their transactions. Just enter your trade details, and the system will automatically calculate your profit/loss per trade and give you an overall view of your assets and financial performance. No more manual calculations—let the system do the work for you! 📈💰

## Features
- **Profit/Loss Calculation**: Instantly calculates profit or loss for each trade.
- **Transaction Grouping**: Automatically organizes transactions by coin.
- **Asset Overview**: Gives you a real-time snapshot of all your holdings.
- **Web-Based Interface**: Simply open your browser and start tracking!
- **Production-Ready Deployment**: Set up easily with Docker Compose and Docker Swarm.

![image](https://github.com/user-attachments/assets/0e731d6d-b95a-47aa-b745-2a16bd00dfb5)

## Tech Stack & Why We Use It ⚙️
Swing Trade Tracker is built with a powerful, modern stack to keep things **fast, scalable, and reliable**:

- **Django (Backend)** 🐍: Handles business logic, database interactions, and user management effortlessly.
- **FastAPI (API Layer)** ⚡: Designed for high-performance async API calls, making data retrieval blazing fast.
- **PostgreSQL (Database)** 🏛️: A rock-solid relational database for storing and managing all trade data.
- **Redis (Caching)** 🔥: Boosts speed by caching frequently accessed data and reducing database queries.
- **MinIO (Object Storage)** 📦: Efficiently stores and manages coin symbols and other assets.
- **React (Frontend)** ⚛️: Provides a smooth, interactive, and modern web experience for users.
- **Nginx (Frontend Hosting & Routing)** 🌐: Serves the React app efficiently and handles routing like a pro.
- **Docker & Docker Swarm** 🐳: Ensures the app is containerized, scalable, and easy to deploy anywhere.

## Installation
Swing Trade Tracker is a **microservice-based** application that runs seamlessly in **Docker**. You can install it in just a few steps!

### Prerequisites
Before you start, make sure you have these installed:
- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

### Installation Steps
1. **Clone the repository:**
   ```sh
   git clone https://github.com/yourusername/swing-trade-tracker.git
   cd swing-trade-tracker
   ```
2. **Deploy on Docker Swarm**
   ```sh
   docker stack deploy -c docker-compose.yml swing-trade-tracker
   ```
   OR you can deploy using Docker Compose if you want to do some development:
   ```sh
   docker-compose up -d
   ```
3. **Check if everything is running:**
   ```sh
   docker ps
   ```

## Usage
Once the application is up and running, you can start using it right from your browser!

1. Open your browser and go to for the production:
   ```
   http://localhost:3500
   ```
   and for the development: 
   ```
   http://localhost:3600
   ```
   Note that if you want to use the development version with Docker Compose, you should disable the web-security flag to avoid CORS errors
   
3. Signup and Login.
4. Enter your trade transactions.
5. Get instant profit/loss calculations and track your assets like a pro! 🚀

## Configuration
No extra configuration needed—just install and start using!

## Dependencies
- Django
- FastAPI
- PostgreSQL
- Redis
- MinIO
- React
- Nginx
- Docker & Docker Compose

## Contributing 🤝
Want to contribute? That’s awesome! Here’s how you can help:
1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes and commit (`git commit -m 'Added new feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Open a pull request!

## License 📜
Swing Trade Tracker is licensed under the **GNU General Public License (GPL)**. See the [LICENSE](LICENSE) file for full details.

## Contact 📬
Have a question or feature request? Open an issue on [GitHub](https://github.com/yourusername/swing-trade-tracker/issues) and let’s talk! 🚀
