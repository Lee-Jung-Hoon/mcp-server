# Python MCP Server Starter

확장 가능한 **Python 기반 Model Context Protocol(MCP) 서버 기본 구조**입니다. Node.js가 꼭 필요한 상황이 아니라면 Python으로도 충분히 MCP 서버를 만들 수 있습니다. 이 스타터는 처음에는 샘플 tool/resource/prompt만 포함하지만, 추후 기능을 독립 모듈로 계속 추가할 수 있도록 구성했습니다.

## 왜 Python인가요?

- 기존 백엔드, 데이터 처리, AI/ML 코드가 Python이라면 MCP 서버도 Python으로 두는 편이 운영과 확장에 유리합니다.
- MCP Python SDK의 `FastMCP` 스타일을 사용하면 decorator 기반으로 tool, resource, prompt를 간결하게 등록할 수 있습니다.
- 기능 단위 모듈 구조를 유지하면 나중에 DB, 외부 API, 파일 처리, 사내 시스템 연동 등을 분리해서 확장하기 쉽습니다.

## 프로젝트 구조

```text
src/mcp_server_starter/
  __main__.py                 # CLI/stdout-safe stdio 실행 진입점
  config/                     # 환경 변수 및 런타임 설정
  core/                       # 서버 생성, 공통 컨텍스트, 모듈 등록기
  shared/                     # 로깅 등 공통 유틸리티
  features/                   # 기능 단위 구현
    echo/                     # 샘플 echo tool
    health/                   # health tool, server info resource
    planning/                 # 샘플 prompt
scripts/                      # 의존성 없이 실행 가능한 구조 검증 스크립트
tests/                        # 설정/registry 단위 테스트
```

## 포함된 MCP 기능

- `health_check` tool: 서버 상태, 이름, 버전, 체크 시각을 반환합니다.
- `echo` tool: 메시지를 그대로 또는 대문자로 반환하는 샘플 tool입니다.
- `mcp://server/info` resource: 서버 메타데이터를 JSON으로 제공합니다.
- `implementation_plan` prompt: 신규 기능 구현 계획 작성을 돕는 샘플 prompt입니다.

## 시작하기

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
python -m mcp_server_starter
```

MCP Inspector로 확인하려면 빌드된 서버 명령을 Inspector에 다음처럼 연결하면 됩니다.

```bash
npx @modelcontextprotocol/inspector python -m mcp_server_starter
```

## 새 기능 추가 방법

1. `src/mcp_server_starter/features/<feature_name>/` 폴더를 만듭니다.
2. `FeatureModule` 규약에 맞춰 `register(server, context)` 메서드를 가진 모듈 클래스를 작성합니다.
3. 작성한 모듈 인스턴스를 `src/mcp_server_starter/features/__init__.py`의 `FEATURE_MODULES` 튜플에 추가합니다.

예시 tool 모듈 형태:

```python
from dataclasses import dataclass

from mcp_server_starter.core.context import AppContext
from mcp_server_starter.core.registry import FastMCPServer


@dataclass(frozen=True, slots=True)
class MyTool:
    name: str = "tool.my_tool"

    def register(self, server: FastMCPServer, context: AppContext) -> None:
        @server.tool(name="my_tool", description="My new tool")
        def my_tool(value: str) -> str:
            return f"{context.settings.server_name}: {value}"


my_tool = MyTool()
```

## 설계 원칙

- **Feature-first**: 기능별 폴더 안에 관련 tool/resource/prompt를 모읍니다.
- **Registry 기반 확장**: 신규 모듈은 `FEATURE_MODULES`에 추가만 하면 서버에 등록됩니다.
- **공통 컨텍스트 주입**: 설정과 로거를 모든 모듈에서 동일하게 사용합니다.
- **stdio 안전 로깅**: MCP 프로토콜과 충돌하지 않도록 로그는 stderr로 출력합니다.
- **테스트 가능한 코어**: SDK가 없어도 설정/registry 같은 핵심 구조는 단위 테스트와 구조 검증이 가능합니다.
