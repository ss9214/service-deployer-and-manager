"""Repository analyzer - detects web app structure and requirements."""

import os
import json
from pathlib import Path
from typing import Optional, Tuple
from dataclasses import dataclass

from ..config.schemas import RepositoryMetadata, DatabaseType


@dataclass
class AnalysisResult:
    """Result of repository analysis."""

    has_frontend: bool
    has_backend: bool
    needs_database: bool
    frontend_framework: Optional[str] = None
    backend_framework: Optional[str] = None
    database_type: Optional[DatabaseType] = None
    frontend_build_command: Optional[str] = None
    backend_build_command: Optional[str] = None
    install_command: Optional[str] = None
    backend_port: int = 8000
    frontend_dir: Optional[str] = None
    backend_dir: Optional[str] = None
    is_monorepo: bool = False


class RepositoryAnalyzer:
    """Analyzes repository structure to determine deployment requirements."""

    # Frontend indicators
    FRONTEND_FRAMEWORKS = {
        "next": {"package": "next", "build": "npm run build", "framework": "Next.js"},
        "react": {"package": "react", "build": "npm run build", "framework": "React"},
        "vue": {"package": "vue", "build": "npm run build", "framework": "Vue"},
        "nuxt": {"package": "nuxt", "build": "npm run build", "framework": "Nuxt.js"},
        "angular": {"package": "@angular/core", "build": "npm run build", "framework": "Angular"},
        "svelte": {"package": "svelte", "build": "npm run build", "framework": "Svelte"},
        "sveltekit": {"package": "@sveltejs/kit", "build": "npm run build", "framework": "SvelteKit"},
    }

    # Backend indicators
    BACKEND_FRAMEWORKS = {
        "express": {"package": "express", "runtime": "node", "framework": "Express"},
        "nestjs": {"package": "@nestjs/core", "runtime": "node", "framework": "NestJS"},
        "fastify": {"package": "fastify", "runtime": "node", "framework": "Fastify"},
        "fastapi": {"file": "requirements.txt", "content": "fastapi", "framework": "FastAPI"},
        "django": {"file": "requirements.txt", "content": "django", "framework": "Django"},
        "flask": {"file": "requirements.txt", "content": "flask", "framework": "Flask"},
        "gin": {"file": "go.mod", "content": "gin-gonic/gin", "framework": "Gin"},
        "echo": {"file": "go.mod", "content": "labstack/echo", "framework": "Echo"},
        "spring": {"file": "pom.xml", "content": "spring-boot", "framework": "Spring Boot"},
    }

    # Database indicators
    DATABASE_INDICATORS = {
        "postgres": {
            "packages": ["pg", "psycopg2", "psycopg2-binary", "postgres"],
            "type": DatabaseType.POSTGRES,
        },
        "mysql": {"packages": ["mysql", "mysql2", "pymysql", "mysqlclient"], "type": DatabaseType.MYSQL},
        "mongodb": {"packages": ["mongodb", "mongoose", "pymongo"], "type": DatabaseType.MONGODB},
        "redis": {"packages": ["redis", "ioredis"], "type": DatabaseType.REDIS},
    }

    def __init__(self, repo_path: str):
        """Initialize analyzer with repository path."""
        self.repo_path = Path(repo_path)

    def analyze(self) -> AnalysisResult:
        """Perform complete analysis of the repository."""
        # Check for monorepo structure
        frontend_dir, backend_dir = self._detect_monorepo_structure()

        # Analyze frontend
        frontend_info = self._analyze_frontend(frontend_dir or self.repo_path)

        # Analyze backend
        backend_info = self._analyze_backend(backend_dir or self.repo_path)

        # Detect database requirements
        database_info = self._detect_database(backend_dir or self.repo_path)

        return AnalysisResult(
            has_frontend=frontend_info["detected"],
            has_backend=backend_info["detected"],
            needs_database=database_info["detected"],
            frontend_framework=frontend_info.get("framework"),
            backend_framework=backend_info.get("framework"),
            database_type=database_info.get("type"),
            frontend_build_command=frontend_info.get("build_command"),
            backend_build_command=backend_info.get("build_command"),
            install_command=self._detect_install_command(frontend_dir or self.repo_path),
            backend_port=backend_info.get("port", 8000),
            frontend_dir=str(frontend_dir.relative_to(self.repo_path)) if frontend_dir else None,
            backend_dir=str(backend_dir.relative_to(self.repo_path)) if backend_dir else None,
            is_monorepo=(frontend_dir is not None or backend_dir is not None),
        )

    def _detect_monorepo_structure(self) -> Tuple[Optional[Path], Optional[Path]]:
        """Detect if this is a monorepo and find frontend/backend directories."""
        frontend_dir = None
        backend_dir = None

        # Common monorepo patterns
        possible_frontend_paths = ["frontend", "client", "web", "ui", "app", "apps/web", "packages/web"]
        possible_backend_paths = ["backend", "server", "api", "apps/api", "packages/api"]

        for path in possible_frontend_paths:
            candidate = self.repo_path / path
            if candidate.exists() and self._has_package_json(candidate):
                frontend_dir = candidate
                break

        for path in possible_backend_paths:
            candidate = self.repo_path / path
            if candidate.exists() and (
                self._has_package_json(candidate)
                or (candidate / "requirements.txt").exists()
                or (candidate / "go.mod").exists()
                or (candidate / "pom.xml").exists()
            ):
                backend_dir = candidate
                break

        return frontend_dir, backend_dir

    def _analyze_frontend(self, search_path: Path) -> dict:
        """Analyze frontend framework and configuration."""
        package_json_path = search_path / "package.json"

        if not package_json_path.exists():
            return {"detected": False}

        try:
            with open(package_json_path, "r") as f:
                package_json = json.load(f)

            dependencies = {**package_json.get("dependencies", {}), **package_json.get("devDependencies", {})}

            # Detect framework
            for key, info in self.FRONTEND_FRAMEWORKS.items():
                if info["package"] in dependencies:
                    return {
                        "detected": True,
                        "framework": info["framework"],
                        "build_command": package_json.get("scripts", {}).get("build", info["build"]),
                    }

            # Generic frontend project (has package.json with build script)
            if "build" in package_json.get("scripts", {}):
                return {
                    "detected": True,
                    "framework": "Node.js",
                    "build_command": "npm run build",
                }

        except (json.JSONDecodeError, KeyError):
            pass

        return {"detected": False}

    def _analyze_backend(self, search_path: Path) -> dict:
        """Analyze backend framework and configuration."""
        # Check for Node.js backend
        package_json_path = search_path / "package.json"
        if package_json_path.exists():
            try:
                with open(package_json_path, "r") as f:
                    package_json = json.load(f)

                dependencies = {**package_json.get("dependencies", {}), **package_json.get("devDependencies", {})}

                for key, info in self.BACKEND_FRAMEWORKS.items():
                    if info.get("runtime") == "node" and info["package"] in dependencies:
                        return {
                            "detected": True,
                            "framework": info["framework"],
                            "build_command": package_json.get("scripts", {}).get("build"),
                            "port": self._extract_port_from_package(package_json),
                        }
            except (json.JSONDecodeError, KeyError):
                pass

        # Check for Python backend
        requirements_txt = search_path / "requirements.txt"
        if requirements_txt.exists():
            content = requirements_txt.read_text()
            for key, info in self.BACKEND_FRAMEWORKS.items():
                if info.get("file") == "requirements.txt" and info["content"] in content.lower():
                    return {
                        "detected": True,
                        "framework": info["framework"],
                        "build_command": None,
                        "port": 8000,
                    }

        # Check for Go backend
        go_mod = search_path / "go.mod"
        if go_mod.exists():
            content = go_mod.read_text()
            for key, info in self.BACKEND_FRAMEWORKS.items():
                if info.get("file") == "go.mod" and info["content"] in content:
                    return {
                        "detected": True,
                        "framework": info["framework"],
                        "build_command": "go build",
                        "port": 8080,
                    }

        # Check for Java/Kotlin backend
        pom_xml = search_path / "pom.xml"
        if pom_xml.exists():
            content = pom_xml.read_text()
            for key, info in self.BACKEND_FRAMEWORKS.items():
                if info.get("file") == "pom.xml" and info["content"] in content:
                    return {
                        "detected": True,
                        "framework": info["framework"],
                        "build_command": "mvn package",
                        "port": 8080,
                    }

        return {"detected": False}

    def _detect_database(self, search_path: Path) -> dict:
        """Detect database requirements."""
        # Check package.json
        package_json_path = search_path / "package.json"
        if package_json_path.exists():
            try:
                with open(package_json_path, "r") as f:
                    package_json = json.load(f)

                dependencies = {**package_json.get("dependencies", {}), **package_json.get("devDependencies", {})}

                for db_name, db_info in self.DATABASE_INDICATORS.items():
                    for package in db_info["packages"]:
                        if package in dependencies:
                            return {"detected": True, "type": db_info["type"]}
            except (json.JSONDecodeError, KeyError):
                pass

        # Check requirements.txt
        requirements_txt = search_path / "requirements.txt"
        if requirements_txt.exists():
            content = requirements_txt.read_text().lower()
            for db_name, db_info in self.DATABASE_INDICATORS.items():
                for package in db_info["packages"]:
                    if package in content:
                        return {"detected": True, "type": db_info["type"]}

        # Check go.mod
        go_mod = search_path / "go.mod"
        if go_mod.exists():
            content = go_mod.read_text().lower()
            for db_name, db_info in self.DATABASE_INDICATORS.items():
                for package in db_info["packages"]:
                    if package in content:
                        return {"detected": True, "type": db_info["type"]}

        return {"detected": False}

    def _detect_install_command(self, search_path: Path) -> Optional[str]:
        """Detect the appropriate install command."""
        if (search_path / "package-lock.json").exists():
            return "npm install"
        elif (search_path / "yarn.lock").exists():
            return "yarn install"
        elif (search_path / "pnpm-lock.yaml").exists():
            return "pnpm install"
        elif (search_path / "requirements.txt").exists():
            return "pip install -r requirements.txt"
        elif (search_path / "go.mod").exists():
            return "go mod download"
        elif (search_path / "pom.xml").exists():
            return "mvn install"

        return None

    def _has_package_json(self, path: Path) -> bool:
        """Check if directory has package.json."""
        return (path / "package.json").exists()

    def _extract_port_from_package(self, package_json: dict) -> int:
        """Try to extract port from package.json scripts or config."""
        # Check scripts for PORT environment variable
        scripts = package_json.get("scripts", {})
        for script in scripts.values():
            if "PORT=" in script:
                try:
                    port_str = script.split("PORT=")[1].split()[0]
                    return int(port_str)
                except (IndexError, ValueError):
                    pass

        # Default to 3000 for frontend, 8000 for backend
        return 8000
