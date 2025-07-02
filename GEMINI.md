이 프로젝트는 AWS 리소스를 나열하고 정리하는 스크립트입니다. `uv`를 패키지 매니저로 사용합니다.

## Rules

- `uv` 가상환경과 package mangaer를 사용할 것.
- 항상 마무리 단계로 `pytest`, `isort`, `black`을 동시에 통과하는 것을 확인하고, 통과하지 못했을 때, 통과할 때 까지 코드를 수정할 것.
- `boto3`, `AWS`, `Python` 등의 패키징 공식 Best Practice를 준수할 것.
- 타입 힌트, 순수 함수, 모듈화로 가독성과 확장성을 유지할 것.
- `README.md`를 기능 변경 시 항상 갱신.
- 기능 개발이나 수정이 완료된 항목과 같은 변경 이력은 `CHANGELOG.md` 파일에 추가할 것
- 커밋 메시지는 항상 영어로 작성할 것.
- 커밋 메시지는 `type(scope): subject` 형식으로 작성하며, `type`은 `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore` 중 하나를 사용하고, `scope`는 선택 사항입니다. `subject`는 변경 내용을 간결하게 요약합니다. (예: `feat(auth): Add user authentication`)
- `release-please-action`을 사용하므로, 커밋 메시지는 [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) 사양을 따릅니다.

## Basic-Check-List

- [x] poetry 환경을 따를 것
- [x] 커밋 컨벤션을 따를 것 ex) feature, docs, fix, refactor, chore 등
- [x] README.md 파일에 항상 최신의 프로젝트에 대한 설명으로 갱신시킬것
- [x] 가독성, 유지보수성, 확장성을 고려한 코드를 작성할 것
- [x] 공식문서와 Best Practice를 따를 것
- [x] black, isort, pytest를 항상 통과할 것
- [ ] 태그 버전은 `vX.Y.Z` 형식으로 작성할 것
- [ ] 릴리즈도 태그 버전의 형식과 동일하게 `vX.Y.Z` 형식으로 작성할 것

## Problem

- 현재 security group 리소스 조회 기능이 구현되어 있지 않음

## requirements

- 현재 프로젝트 구조와 코드에 맞게 AWS Security Group의 리소스를 조회하는 기능 추가 (0.0.0.0/0 AnyOpen된 Inbound Rule을 가진 Security Group은 특별히 표시할 것)

## result

- Security Group 리소스 조회 기능 추가 완료
- 0.0.0.0/0 AnyOpen된 Inbound Rule을 가진 Security Group은 '⚠️ YES'로 표시
- 프로젝트 구조와 코드 스타일에 맞게 구현
- README.md 파일 업데이트 완료