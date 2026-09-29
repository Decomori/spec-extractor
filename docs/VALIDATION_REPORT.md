# 수정 후 검증 — v0.1.1 (2026-09-29)

환경: macOS, Python 3.12.14. 구조 검증 통과, 전체 테스트 **38개 통과**.
추가 회귀 테스트로 수정 전 실패와 수정 후 통과를 확인했습니다.
네트워크 테스트는 모의 응답, 설치 테스트는 임시 홈 폴더를 사용했습니다.
실제 앱 활성화·AI 출력 품질·실사이트 크롤링은 검증하지 않았습니다.
변경 상세는 CHANGELOG.md의 0.1.1 항목을 참고하세요.

---

아래는 최초 ZIP에 포함된 이전 검증 기록입니다.

# 실제 검증 결과 — spec-extractor v0.1.0

검증일: 2026-09-29. 환경: Python 3.13.5, Linux x86_64.

## 완료

- 구조 검증 통과: 독립 플러그인 1개, 스킬 1개, 상대 경로, JSON/Python 문법.
- 자동 테스트 **35개 통과**, 실패 0개.
- 설치/업데이트/삭제 테스트는 임시 홈 폴더에서만 실행. 실제 사용자 앱 설정은 변경하지 않음.
- 공개 업로드 파일 목록 생성(`--plan`) 성공. 해당 명령은 GitHub 네트워크 호출 없이 실행.
- 기능별 검증: 누락·충돌·변형 구분, 실제 예제의 인용 일치, 출처 ID와 위치 검사, CSV 수식 방어, BOM 출력과 미확정 값 보존.

## 검증하지 않은 범위

- 실제 사용자의 macOS/Windows, 다른 GPT 계정, ChatGPT/Codex UI 설치·활성화.
- 실제 LLM의 스킬 선택·출처 해석·스캔 정확도·이미지 생성 품질.
- 외부 이미지 API 호출, 실사이트 부하·렌더링·검색엔진 순위, 모든 OS/버전 조합.
- GitHub 저장소 생성/업로드와 공개 디렉터리 제출·승인.

예제 데이터는 합성 자료입니다. 자동 테스트 통과가 제품 사진의 상업적 정확성이나
실제 검색 노출·모든 호스트의 호환성을 보증하지 않습니다.

## Test output

```text
test_conflicting_catalog_refused (test_package.PackageTests.test_conflicting_catalog_refused) ... ok
test_exactly_one_skill (test_package.PackageTests.test_exactly_one_skill) ... ok
test_existing_install_requires_replace (test_package.PackageTests.test_existing_install_requires_replace) ... ok
test_failed_copy_does_not_delete_existing (test_package.PackageTests.test_failed_copy_does_not_delete_existing) ... ok
test_install_preserves_other_settings (test_package.PackageTests.test_install_preserves_other_settings) ... ok
test_lock_prevents_concurrent_install (test_package.PackageTests.test_lock_prevents_concurrent_install) ... ok
test_publisher_excludes_runtime_data (test_package.PackageTests.test_publisher_excludes_runtime_data) ... ok
test_publisher_plan_is_offline (test_package.PackageTests.test_publisher_plan_is_offline) ... ok
test_publisher_rejects_secret (test_package.PackageTests.test_publisher_rejects_secret) ... ok
test_skill_mode_is_standalone (test_package.PackageTests.test_skill_mode_is_standalone) ... ok
test_structure (test_package.PackageTests.test_structure) ... ok
test_symlink_parent_refused (test_package.PackageTests.test_symlink_parent_refused) ... ok
test_uninstall_needs_confirmation (test_package.PackageTests.test_uninstall_needs_confirmation) ... ok
test_uninstall_only_own_plugin (test_package.PackageTests.test_uninstall_only_own_plugin) ... ok
test_unmanaged_folder_refused (test_package.PackageTests.test_unmanaged_folder_refused) ... ok
test_update_backs_up_outside_discovery (test_package.PackageTests.test_update_backs_up_outside_discovery) ... ok
test_boolean_not_page_number (test_specs.SpecificationTests.test_boolean_not_page_number) ... ok
test_broken_reference (test_specs.SpecificationTests.test_broken_reference) ... ok
test_conflict_candidate_evidence (test_specs.SpecificationTests.test_conflict_candidate_evidence) ... ok
test_conflict_candidates_required (test_specs.SpecificationTests.test_conflict_candidates_required) ... ok
test_derived_formula_required (test_specs.SpecificationTests.test_derived_formula_required) ... ok
test_duplicate_field_rejected (test_specs.SpecificationTests.test_duplicate_field_rejected) ... ok
test_duplicate_variant_rejected (test_specs.SpecificationTests.test_duplicate_variant_rejected) ... ok
test_export_bom_conflicts_and_no_overwrite (test_specs.SpecificationTests.test_export_bom_conflicts_and_no_overwrite) ... ok
test_formula_escape (test_specs.SpecificationTests.test_formula_escape) ... ok
test_locator_required (test_specs.SpecificationTests.test_locator_required) ... ok
test_nonfinite_rejected (test_specs.SpecificationTests.test_nonfinite_rejected) ... ok
test_one_based_page (test_specs.SpecificationTests.test_one_based_page) ... ok
test_quote_required (test_specs.SpecificationTests.test_quote_required) ... ok
test_real_fixture_quotes_match (test_specs.SpecificationTests.test_real_fixture_quotes_match) ... ok
test_same_product_different_variant_allowed (test_specs.SpecificationTests.test_same_product_different_variant_allowed) ... ok
test_source_required (test_specs.SpecificationTests.test_source_required) ... ok
test_unresolved_not_guessed (test_specs.SpecificationTests.test_unresolved_not_guessed) ... ok
test_valid_fixture (test_specs.SpecificationTests.test_valid_fixture) ... ok
test_wrong_type_is_error_not_crash (test_specs.SpecificationTests.test_wrong_type_is_error_not_crash) ... ok

----------------------------------------------------------------------
Ran 35 tests in 0.046s

OK
```
