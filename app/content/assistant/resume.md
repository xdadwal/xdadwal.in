# Akshay Dadwal — Software Engineer

Email: akshayd00@outlook.com
Location: New Delhi, India

## Profile

A Software Engineer with 7 years of experience building solutions for complex B2B and B2C
systems. Working with multiple startups, I have led and delivered several end-to-end products,
covering requirement gathering, system design docs, cloud infra setup, stakeholder management,
mentoring peers and code reviews.

## Skills

Django, Python, FastAPI, PostgreSQL, Celery, Redis, JavaScript, Node.js, Express.js, MongoDB,
Kafka, Pub/Sub, AWS, GCP

## Professional Experience

### Detect Technologies Inc. — Halifax, Canada (Remote)

AI-powered utility asset management: inspects transmission powerlines across Canada, capturing
images with guided drones and running health checks with in-house OpenCV models.

#### Software Development Engineer - III (May 2025 – Present)

- Leading technical integration with Nova Scotia Power, one of the largest electrical power
  companies in Canada.

### Attentive.ai — Noida, India

AI-driven SaaS: automated property measurements from aerial images with in-house OpenCV models,
and the Accelerate platform for managing the day-to-day operations of US landscaping companies.

#### Software Engineer - III (Jan 2025 – Mar 2025)

- With the AI team, built a backend service that extracts and parses text from PDF files and
  serves real-time search queries from Feathers (Attentive's internal annotation platform).

#### Software Engineer - II (Jan 2022 – Dec 2024)

- Led the low- and high-level design and development of the Operations module backend (Django,
  PostgreSQL, Celery, Redis): tracking project revenue and cost, scheduling tasks with a custom
  calendar, and time tracking that computes employees' payroll.
- Designed and built an extensible user management service that authenticates and authorizes
  public and private cross-service API calls to prevent data leakage between tenants, with role-
  and attribute-based access control written as an abstraction over Django's permission framework.
- Integrated New Relic, found bottlenecks in APIs and DB queries, and optimized Django ORM queries
  to cut network I/O, improving latency by ~20-40% on several APIs.
- Contributed to the Residential microservice (Express.js, MongoDB), which integrates in-house and
  third-party geospatial AI services for automated residential property measurements.
- Designed and implemented near real-time event processing in the Residential microservice with
  GCP Pub/Sub and Cloud Functions, running workflows such as notifications, background jobs and
  data aggregation.
- Also managed stakeholders, sprints and deployments, did peer code reviews and enforced standard
  Python and Django practices.

### Renewbuy.com — Gurgaon, India

Insurance aggregation platform: a simpler insurance buying experience for customers, plus a sales
performance dashboard and related services for certified insurance agents.

#### Senior Software Engineer (Apr 2021 – Jan 2022)

- Designed and built an OTP generation and verification microservice in FastAPI, to which all
  internal services delegate OTP operations, and published a Python package for integrating with it.
- Set up monitoring and alerting on several backend services with DataDog and identified
  bottlenecks such as the slowest DB queries and APIs.
- Identified DB issues and cross-service network calls and wrote a strategy document for
  optimizing those APIs, improving overall latency by ~30%.
- Designed a near real-time data ingestion pipeline (Debezium, Kafka, AWS Redshift, Lambda) that
  captures transactional data from multiple sources, transforms it and loads it into the OLAP
  backend in batches.

#### Software Engineer (Aug 2018 – Apr 2021)

- Designed the architecture revamp of the Life Insurance platform to simplify integrations with
  third-party insurers, and implemented complex new product features that contributed
  significantly to the company's revenue.
- Designed and built a wallet / payment gateway aggregator microservice in Django for a seamless
  payment experience, reducing drop-off rates by ~15%.
- Maintained the user onboarding and KYC platform, adding features and writing data extraction
  scripts for annual IRDAI audits.
- Ran a security audit of self-managed and AWS infrastructure and production web applications with
  a third-party vendor, found severe security issues and patched them with multiple teams.
- Managed AWS infrastructure, proactively checking for bottlenecks in RDS, EC2, SQS and other
  services.

## Awards

- Tech Trendsetter, Attentive.ai (Nov 2024): annual award for exploring new technologies,
  improving system observability and writing technical documentation for peers.
- Innovation, Attentive.ai (Dec 2022): annual award for proactively finding system bottlenecks,
  designing innovative solutions to complex business problems and implementing robust, scalable
  solutions.
- Rockstar Rookie, D2C Consulting (Renewbuy.com) (Apr 2019): quarterly award for performing
  exceptionally as a new joiner, adapting quickly and contributing significantly to several
  products.

## Education

- B.Tech - Information Technology, HMRITM, Delhi, India (2014 – 2018)

## Personal Projects

### dex-cli

A command-line Python tool to download and manage manga and comics from various platforms. It
supports mangadex.org, uses multi-threading for concurrent downloads without blocking on I/O, uses
the Factory design pattern so more providers can be added, and has unit tests with ~60% coverage.
Planned: cloud storage integration, and a better pagination strategy for third-party APIs.

## Volunteer Experience

- Mentor, Exercism (2023 – present): in my free time, helping new Python programmers with their
  questions and giving constructive feedback in code reviews.
