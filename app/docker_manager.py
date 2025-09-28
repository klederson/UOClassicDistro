from __future__ import annotations

from typing import Dict, Optional

import docker
from docker.errors import NotFound

from .config import settings


def _parse_ports(ports_str: str) -> Dict[str, int]:
    mapping: Dict[str, int] = {}
    if not ports_str:
        return mapping
    parts = [p.strip() for p in ports_str.split(",") if p.strip()]
    for part in parts:
        host, container = part.split(":", 1)
        mapping[f"{container}/tcp"] = int(host)
    return mapping


def _parse_env(env_str: Optional[str]) -> Dict[str, str]:
    env: Dict[str, str] = {}
    if not env_str:
        return env
    pairs = [p.strip() for p in env_str.split(",") if p.strip()]
    for pair in pairs:
        key, value = pair.split("=", 1)
        env[key] = value
    return env


def _parse_volumes(volumes_str: Optional[str]):
    volumes = {}
    if not volumes_str:
        return volumes
    parts = [p.strip() for p in volumes_str.split(",") if p.strip()]
    for part in parts:
        # host:container[:mode]
        segments = part.split(":")
        if len(segments) == 2:
            host, container = segments
            mode = "rw"
        else:
            host, container, mode = segments
        volumes[host] = {"bind": container, "mode": mode}
    return volumes


def get_client() -> docker.DockerClient:
    return docker.from_env()


def ensure_container():
    client = get_client()
    try:
        container = client.containers.get(settings.managed_name)
        return container
    except NotFound:
        container = client.containers.run(
            settings.managed_image,
            name=settings.managed_name,
            detach=True,
            ports=_parse_ports(settings.managed_ports),
            environment=_parse_env(settings.managed_env),
            volumes=_parse_volumes(settings.managed_volumes),
            restart_policy={"Name": "unless-stopped"},
        )
        return container


def start_container():
    client = get_client()
    try:
        container = client.containers.get(settings.managed_name)
        if container.status != "running":
            container.start()
        return True
    except NotFound:
        ensure_container()
        return True


def stop_container():
    client = get_client()
    try:
        container = client.containers.get(settings.managed_name)
        if container.status == "running":
            container.stop()
        return True
    except NotFound:
        return False


def get_status() -> dict:
    client = get_client()
    try:
        container = client.containers.get(settings.managed_name)
        container.reload()
        return {
            "name": settings.managed_name,
            "image": container.image.tags[0] if container.image.tags else settings.managed_image,
            "status": container.status,
            "id": container.id[:12],
        }
    except NotFound:
        return {
            "name": settings.managed_name,
            "image": settings.managed_image,
            "status": "not_created",
            "id": None,
        }


def get_logs(tail: int = 200) -> str:
    client = get_client()
    try:
        container = client.containers.get(settings.managed_name)
        return container.logs(tail=tail).decode("utf-8", errors="ignore")
    except NotFound:
        return ""

