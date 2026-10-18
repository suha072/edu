# edu

휴대폰과 태블릿에서 터치로 쓰는 HTML 교재를 모아 GitHub Pages로 배포하는 저장소입니다.
`main` 브랜치에 push하면 GitHub Actions가 교재 목록 페이지를 새로 만들고 사이트에 배포합니다.

- 교재 목록: https://suha072.github.io/edu/
- 교재 하나의 주소: `https://suha072.github.io/edu/<폴더 이름>/` (예: https://suha072.github.io/edu/stacking-cubes/)

## 폴더 구조

| 경로 | 내용 |
| --- | --- |
| `materials/<폴더 이름>/index.html` | 교재 하나. 그림 같은 부속 파일도 같은 폴더에 둡니다. |
| `scripts/build_site.py` | `materials/`를 `_site/`로 복사하고 교재 목록 페이지 `_site/index.html`을 만듭니다. |
| `.github/workflows/pages.yml` | `main`에 push하면 `build_site.py`를 실행하고 `_site/`를 Pages에 배포합니다. |

## 교재 추가하기

1. `materials/` 아래에 새 폴더를 만듭니다. 폴더 이름은 주소에 그대로 쓰이므로 영어 소문자, 숫자, 하이픈만 씁니다(예: `fraction-pizza`). 규칙에 맞지 않으면 빌드가 실패합니다.
2. 교재 HTML 파일을 그 폴더에 `index.html`이라는 이름으로 넣습니다.
3. 목록 카드에 보일 제목은 `<title>`에서, 설명은 `<meta name="description" content="...">`에서 읽습니다. 설명 태그가 없으면 카드에 제목과 날짜만 보입니다.
4. 커밋하고 `main`에 push합니다. 1~2분 뒤 저장소의 Actions 탭에서 배포가 끝났는지 확인합니다.

목록은 교재 폴더를 처음 커밋한 날짜 순서로, 최근 교재가 위에 오도록 정렬됩니다.

## 내 컴퓨터에서 미리 보기

```bash
python3 scripts/build_site.py
python3 -m http.server -d _site 8000
```

브라우저에서 http://localhost:8000 을 엽니다. 같은 Wi-Fi에 있는 태블릿에서는 `http://<컴퓨터 IP>:8000`으로 열 수 있습니다.

## 처음 한 번만 하는 설정

1. 저장소가 private이면 GitHub 무료 요금제에서는 Pages를 쓸 수 없습니다. Settings → General → Danger Zone에서 저장소를 public으로 바꾸거나 GitHub Pro를 사용합니다.
2. Settings → Pages → Build and deployment의 Source를 **GitHub Actions**로 선택합니다.
3. Actions 탭에서 `GitHub Pages 배포` 워크플로를 다시 실행하거나 새로 push합니다.
