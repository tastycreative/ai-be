# Python Application for EC2 and Docker

This project contains a Python Flask application containerized with Docker, ready for deployment on AWS EC2.

## Local Development

### Prerequisites
- Python 3.11+
- Docker and Docker Compose

### Run Locally (without Docker)
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

Visit `http://localhost:8000`

### Run with Docker
```bash
# Build and run with Docker Compose
docker-compose up --build

# Or build and run manually
docker build -t ai-be .
docker run -p 8000:8000 ai-be
```

## EC2 Deployment

### Option 1: Docker on EC2

1. **Launch EC2 Instance**
   - AMI: Amazon Linux 2023 or Ubuntu 22.04
   - Instance type: t2.micro (or larger)
   - Security Group: Allow inbound TCP on port 8000

2. **SSH into EC2**
   ```bash
   ssh -i your-key.pem ec2-user@your-ec2-ip
   ```

3. **Install Docker**
   ```bash
   # For Amazon Linux 2023
   sudo yum update -y
   sudo yum install -y docker
   sudo systemctl start docker
   sudo systemctl enable docker
   sudo usermod -a -G docker ec2-user

   # Install Docker Compose
   sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose

   # Log out and back in for group changes to take effect
   exit
   ```

4. **Deploy Application**
   ```bash
   # Clone or upload your code
   git clone <your-repo-url>
   cd ai-be

   # Build and run
   docker-compose up -d
   ```

5. **Access Application**
   ```
   http://your-ec2-public-ip:8000
   ```

### Option 2: Direct Python Installation on EC2

1. **SSH into EC2 and Install Python**
   ```bash
   # For Amazon Linux 2023
   sudo yum update -y
   sudo yum install -y python3.11 python3.11-pip git

   # For Ubuntu
   sudo apt update
   sudo apt install -y python3.11 python3.11-venv python3-pip git
   ```

2. **Deploy Application**
   ```bash
   # Clone repository
   git clone <your-repo-url>
   cd ai-be

   # Create virtual environment
   python3.11 -m venv venv
   source venv/bin/activate

   # Install dependencies
   pip install -r requirements.txt

   # Run with gunicorn (production)
   gunicorn -w 4 -b 0.0.0.0:8000 app:app
   ```

3. **Run as System Service (Optional)**
   Create `/etc/systemd/system/ai-be.service`:
   ```ini
   [Unit]
   Description=AI Backend Service
   After=network.target

   [Service]
   User=ec2-user
   WorkingDirectory=/home/ec2-user/ai-be
   ExecStart=/home/ec2-user/ai-be/venv/bin/gunicorn -w 4 -b 0.0.0.0:8000 app:app
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

   Enable and start:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable ai-be
   sudo systemctl start ai-be
   ```

## Docker Commands

```bash
# Build image
docker build -t ai-be .

# Run container
docker run -d -p 8000:8000 --name ai-be-container ai-be

# View logs
docker logs ai-be-container

# Stop container
docker stop ai-be-container

# Remove container
docker rm ai-be-container

# Push to Docker Hub
docker tag ai-be your-dockerhub-username/ai-be:latest
docker push your-dockerhub-username/ai-be:latest
```

## Environment Variables

Create a `.env` file for environment-specific configuration:
```
ENVIRONMENT=production
PORT=8000
```

## API Endpoints

- `GET /` - Main endpoint
- `GET /health` - Health check endpoint

## GitHub Actions CI/CD

This project includes automated CI/CD pipeline using GitHub Actions.

### Setup GitHub Secrets

Configure the following secrets in your GitHub repository (Settings → Secrets and variables → Actions):

#### Docker Hub
- `DOCKERHUB_USERNAME` - Your Docker Hub username
- `DOCKERHUB_TOKEN` - Docker Hub access token (create at hub.docker.com/settings/security)

#### AWS Credentials
- `AWS_ACCESS_KEY_ID` - AWS access key with EC2 permissions
- `AWS_SECRET_ACCESS_KEY` - AWS secret access key

#### EC2 Deployment
- `EC2_HOST` - Your EC2 instance public IP or hostname
- `EC2_USER` - SSH user (usually `ec2-user` or `ubuntu`)
- `SSH_PRIVATE_KEY` - Your EC2 private key content (entire .pem file)

### Pipeline Workflow

The CI/CD pipeline runs on every push to `main` or `develop` branches:

1. **Test** - Runs linting and tests
2. **Build** - Builds and pushes Docker image to Docker Hub
3. **Deploy** - Deploys to EC2 (only on `main` branch)

### First-time EC2 Setup for CI/CD

Prepare your EC2 instance for automated deployments:

```bash
# SSH into your EC2 instance
ssh -i your-key.pem ec2-user@your-ec2-ip

# Install Docker (if not already installed)
sudo yum update -y
sudo yum install -y docker git
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -a -G docker ec2-user

# Log out and back in
exit
ssh -i your-key.pem ec2-user@your-ec2-ip

# Clone your repository
cd ~
git clone https://github.com/your-username/ai-be.git
cd ai-be

# Configure git (for automated pulls)
git config pull.rebase false
```

### Manual Deployment

Push to GitHub and the pipeline will automatically:
```bash
git add .
git commit -m "Deploy updates"
git push origin main
```

Watch the deployment at: `https://github.com/your-username/ai-be/actions`

## Security Considerations

- Update security group rules to restrict access as needed
- Use environment variables for sensitive data
- Consider using AWS Secrets Manager or Parameter Store
- Enable HTTPS using ALB or nginx reverse proxy
- Keep dependencies updated regularly
- Rotate AWS credentials and SSH keys periodically
- Use GitHub Environments for additional deployment protection
