def _create_uploaded_asset(client, filename="IMG_TEST.jpg"):
    presign_response = client.post(
        "/api/v1/uploads/presign",
        json={
            "filename": filename,
            "contentType": "image/jpeg",
            "bizType": "detection-image",
        },
    )
    assert presign_response.status_code == 200
    presign_payload = presign_response.json()["data"]

    upload_response = client.put(
        f"/api/v1/uploads/files/{presign_payload['assetId']}",
        content=b"fake-image-bytes",
        headers={"content-type": "image/jpeg"},
    )
    assert upload_response.status_code == 200
    return presign_payload["assetId"]


def test_healthcheck_returns_envelope(client):
    response = client.get("/healthz")

    assert response.status_code == 200
    payload = response.json()

    assert payload["code"] == "OK"
    assert payload["data"]["status"] == "ok"
    assert payload["data"]["service"] == "Gujian Platform Backend"
    assert "requestId" in payload
    assert response.headers["x-request-id"] == payload["requestId"]


def test_healthcheck_respects_incoming_request_id(client):
    response = client.get("/healthz", headers={"x-request-id": "req-phase1"})

    assert response.status_code == 200
    assert response.json()["requestId"] == "req-phase1"
    assert response.headers["x-request-id"] == "req-phase1"


def test_cors_allows_vite_fallback_ports(client):
    response = client.options(
        "/api/v1/detection/batches?limit=12",
        headers={
            "origin": "http://127.0.0.1:5174",
            "access-control-request-method": "GET",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://127.0.0.1:5174"


def test_api_registry_lists_phase_one_slots(client):
    response = client.get("/api/v1")

    assert response.status_code == 200
    payload = response.json()["data"]
    modules = {module["name"]: module for module in payload["modules"]}

    assert modules["overview"]["routeFile"] == "backend/app/api/v1/overview.py"
    assert modules["overview"]["moduleDir"] == "backend/app/modules/overview"
    assert modules["overview"]["modulePackage"] == "backend.app.modules.overview"
    assert modules["overview"]["mountPath"] == "/pages/overview"
    assert modules["overview"]["registered"] is True

    assert modules["twin"]["routeFile"] == "backend/app/api/v1/twin.py"
    assert modules["twin"]["moduleDir"] == "backend/app/modules/twin"
    assert modules["twin"]["modulePackage"] == "backend.app.modules.twin"
    assert modules["twin"]["mountPath"] == "/pages/twin"
    assert modules["twin"]["registered"] is True

    assert modules["detection"]["routeFile"] == "backend/app/api/v1/detection.py"
    assert modules["detection"]["moduleDir"] == "backend/app/modules/detection"
    assert modules["detection"]["modulePackage"] == "backend.app.modules.detection"
    assert modules["detection"]["mountPath"] == "/detection"
    assert modules["detection"]["registered"] is True


def test_api_registry_includes_service_metadata(client):
    response = client.get("/api/v1")

    assert response.status_code == 200
    payload = response.json()["data"]

    assert payload["service"] == "Gujian Platform Backend"
    assert payload["version"] == "0.1.0"


def test_phase_one_module_directories_exist():
    from pathlib import Path

    backend_dir = Path(__file__).resolve().parents[1]

    assert (backend_dir / "app" / "modules" / "overview").is_dir()
    assert (backend_dir / "app" / "modules" / "twin").is_dir()
    assert (backend_dir / "app" / "modules" / "detection").is_dir()
    assert (backend_dir / "app" / "modules" / "knowledge").is_dir()
    assert (backend_dir / "app" / "modules" / "screen").is_dir()


def test_overview_page_returns_phase_one_payload(client):
    response = client.get("/api/v1/pages/overview")

    assert response.status_code == 200
    payload = response.json()["data"]

    assert len(payload["heroMetrics"]) == 4
    assert payload["archiveNodes"][0]["name"] == "东南外槽柱组"
    assert payload["issueRanking"][0]["name"] == "木构裂缝"
    assert payload["regionalHealth"][0]["region"] == "佛宫寺核心保护范围"
    assert payload["workOrders"][0] == {"stage": "巡检影像入库", "done": 18, "total": 18}
    assert payload["overviewBriefings"][0]["status"] == "病害识别已回写"
    assert payload["coordinationEvents"][0]["module"] == "病害检测"


def test_twin_page_returns_site_payload(client):
    response = client.get("/api/v1/pages/twin", params={"siteId": "site_001"})

    assert response.status_code == 200
    payload = response.json()["data"]

    assert payload["site"]["id"] == "site_001"
    assert payload["site"]["name"] == "应县木塔（佛宫寺释迦塔）"
    assert payload["defaultDamageId"] == "damage-east-pillar-crack"
    assert payload["components"][0]["lastInspection"] == "2026-03-10 14:20"
    assert payload["damagePoints"][0]["inspectedAt"] == "2026-03-11 08:16"
    assert payload["damagePoints"][0]["componentId"] == "component-pillar-east"


def test_twin_page_returns_404_for_unknown_site(client):
    response = client.get("/api/v1/pages/twin", params={"siteId": "missing_site"})

    assert response.status_code == 404
    assert response.json()["detail"] == "未找到编号为 missing_site 的古建站点。"


def test_twin_page_builds_archive_for_uploaded_building(client):
    asset_id = _create_uploaded_asset(client, "IMG_ARCHIVE_SITE.jpg")
    create_response = client.post(
        "/api/v1/detection/batches",
        json={
            "siteId": "应县木塔",
            "componentId": "南立面斗栱",
            "assetIds": [asset_id],
            "source": "ground",
            "capturedAt": "2026-03-15T10:05:00+08:00",
        },
    )
    assert create_response.status_code == 201

    import time

    time.sleep(2.2)

    response = client.get("/api/v1/pages/twin", params={"siteId": "应县木塔"})

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["site"]["name"] == "应县木塔"
    assert payload["components"][0]["name"] == "南立面斗栱"
    assert payload["damagePoints"]


def test_detection_batch_create_and_read_round_trip(client):
    create_response = client.post(
        "/api/v1/detection/batches",
        json={
            "siteId": "site_001",
            "componentId": "component-pillar-east",
            "assetIds": ["asset_capture_001"],
            "source": "ground",
            "capturedAt": "2026-03-15T10:05:00+08:00",
        },
    )

    assert create_response.status_code == 201
    create_payload = create_response.json()["data"]
    assert create_payload["status"] == "queued"
    assert create_payload["batchId"].startswith("batch_")

    batch_response = client.get(f"/api/v1/detection/batches/{create_payload['batchId']}")

    assert batch_response.status_code == 200
    batch_payload = batch_response.json()["data"]

    assert batch_payload["siteId"] == "site_001"
    assert batch_payload["componentId"] == "component-pillar-east"
    assert batch_payload["status"] == "queued"
    assert batch_payload["progress"] == 33
    assert batch_payload["asset"]["name"] == "asset_capture_001.jpg"
    assert batch_payload["asset"]["statusLabel"] == "已入队，等待模型执行"
    assert batch_payload["tasks"][1]["status"] == "pending"
    assert batch_payload["results"] == []


def test_detection_batch_list_returns_real_batches_without_demo_defaults(client):
    create_response = client.post(
        "/api/v1/detection/batches",
        json={
            "siteId": "site_001",
            "componentId": "component-pillar-east",
            "assetIds": ["asset_recent_001"],
            "source": "ground",
            "capturedAt": "2026-03-15T10:05:00+08:00",
        },
    )

    assert create_response.status_code == 201
    batch_id = create_response.json()["data"]["batchId"]

    list_response = client.get("/api/v1/detection/batches", params={"limit": 5})

    assert list_response.status_code == 200
    payload = list_response.json()["data"]
    batch_ids = [item["batchId"] for item in payload["items"]]

    assert batch_id in batch_ids
    assert all(not item.startswith("batch_demo_") for item in batch_ids)


def test_detection_batch_can_be_deleted_from_history(client):
    create_response = client.post(
        "/api/v1/detection/batches",
        json={
            "siteId": "site_001",
            "componentId": "component-pillar-east",
            "assetIds": ["asset_delete_001"],
            "source": "ground",
            "capturedAt": "2026-03-15T10:05:00+08:00",
        },
    )
    assert create_response.status_code == 201
    batch_id = create_response.json()["data"]["batchId"]

    delete_response = client.delete(f"/api/v1/detection/batches/{batch_id}")
    assert delete_response.status_code == 200
    assert delete_response.json()["data"]["batchId"] == batch_id

    read_response = client.get(f"/api/v1/detection/batches/{batch_id}")
    assert read_response.status_code == 404


def test_detection_batch_persists_across_app_instances():
    from fastapi.testclient import TestClient

    from backend.app.main import create_application

    with TestClient(create_application()) as first_client:
        create_response = first_client.post(
            "/api/v1/detection/batches",
            json={
                "siteId": "site_001",
                "componentId": "component-pillar-east",
                "assetIds": ["asset_persist_001"],
                "source": "ground",
                "capturedAt": "2026-03-15T10:05:00+08:00",
            },
        )

        assert create_response.status_code == 201
        batch_id = create_response.json()["data"]["batchId"]

    with TestClient(create_application()) as second_client:
        read_response = second_client.get(f"/api/v1/detection/batches/{batch_id}")

        assert read_response.status_code == 200
        payload = read_response.json()["data"]
        assert payload["batchId"] == batch_id
        assert payload["asset"]["name"] == "asset_persist_001.jpg"


def test_knowledge_page_returns_payload(client):
    response = client.get("/api/v1/pages/knowledge")

    assert response.status_code == 200
    payload = response.json()["data"]

    assert payload["knowledgeMetrics"][0]["label"] == "处理方法"
    assert payload["knowledgeOverview"][0]["title"] == "病害档案直达处理建议"
    assert payload["knowledgeStandards"][0]["applicableTo"] == "木柱、塔檐、台基、彩画等文物建筑构件"
    assert payload["knowledgeActions"][0]["kind"] == "route"


def test_screen_page_returns_payload(client):
    response = client.get("/api/v1/pages/screen")

    assert response.status_code == 200
    payload = response.json()["data"]

    assert payload["screenMetrics"][0]["label"] == "监管对象"
    assert payload["screenCoverageRegions"][0]["region"] == "佛宫寺核心保护范围"
    assert payload["screenCoverageRegions"][0]["status"] == "critical"
    assert payload["screenAlerts"][0]["severity"] == "high"


def test_upload_presign_returns_payload(client):
    response = client.post(
        "/api/v1/uploads/presign",
        json={
            "filename": "IMG_001.jpg",
            "contentType": "image/jpeg",
            "bizType": "detection-image",
        },
    )

    assert response.status_code == 200
    payload = response.json()["data"]

    assert payload["assetId"].startswith("asset_")
    assert payload["objectKey"].endswith("IMG_001.jpg")
    assert payload["method"] == "PUT"
    assert "/api/v1/uploads/files/" in payload["uploadUrl"]
    assert "mock-storage" not in payload["uploadUrl"]


def test_upload_file_writes_to_local_storage(client):
    from pathlib import Path

    presign_response = client.post(
        "/api/v1/uploads/presign",
        json={
            "filename": "IMG_UPLOAD_TEST.jpg",
            "contentType": "image/jpeg",
            "bizType": "detection-image",
        },
    )

    assert presign_response.status_code == 200
    presign_payload = presign_response.json()["data"]

    upload_response = client.put(
        f"/api/v1/uploads/files/{presign_payload['assetId']}",
        content=b"fake-image-bytes",
        headers={"content-type": "image/jpeg"},
    )

    assert upload_response.status_code == 200
    upload_payload = upload_response.json()["data"]

    assert upload_payload["assetId"] == presign_payload["assetId"]
    assert upload_payload["filename"] == "IMG_UPLOAD_TEST.jpg"
    assert upload_payload["contentType"] == "image/jpeg"
    assert upload_payload["fileSize"] == len(b"fake-image-bytes")
    assert upload_payload["uploadStatus"] == "uploaded"
    uploaded_path = Path("backend/storage/uploads", upload_payload["objectKey"])
    assert uploaded_path.exists()
    uploaded_path.unlink()


def test_uploaded_file_can_be_read_back(client):
    presign_response = client.post(
        "/api/v1/uploads/presign",
        json={
            "filename": "IMG_READ_BACK.jpg",
            "contentType": "image/jpeg",
            "bizType": "detection-image",
        },
    )
    assert presign_response.status_code == 200
    presign_payload = presign_response.json()["data"]

    upload_response = client.put(
        f"/api/v1/uploads/files/{presign_payload['assetId']}",
        content=b"fake-image-bytes",
        headers={"content-type": "image/jpeg"},
    )
    assert upload_response.status_code == 200

    read_response = client.get(f"/api/v1/uploads/files/{presign_payload['assetId']}")

    assert read_response.status_code == 200
    assert read_response.headers["content-type"].startswith("image/jpeg")
    assert read_response.content == b"fake-image-bytes"


def test_detection_batch_advances_after_polling(client):
    asset_id = _create_uploaded_asset(client, "IMG_POLL_001.jpg")

    create_response = client.post(
        "/api/v1/detection/batches",
        json={
            "siteId": "site_001",
            "componentId": "component-pillar-east",
            "assetIds": [asset_id],
            "source": "ground",
            "capturedAt": "2026-03-15T10:05:00+08:00",
        },
    )

    assert create_response.status_code == 201
    batch_id = create_response.json()["data"]["batchId"]

    import time

    time.sleep(2.2)

    read_response = client.get(f"/api/v1/detection/batches/{batch_id}")

    assert read_response.status_code == 200
    payload = read_response.json()["data"]
    assert payload["status"] == "completed"
    assert len(payload["results"]) == 3
    assert {item["modelVersion"] for item in payload["results"]} == {"local-rule-based-v1"}

    result_id = payload["results"][0]["id"]
    overview_payload = client.get("/api/v1/pages/overview").json()["data"]
    twin_payload = client.get("/api/v1/pages/twin", params={"siteId": "site_001"}).json()["data"]
    screen_payload = client.get("/api/v1/pages/screen").json()["data"]
    knowledge_payload = client.get("/api/v1/pages/knowledge").json()["data"]

    assert any(result_id in event["detail"] for event in overview_payload["coordinationEvents"])
    assert any(point["id"] == result_id for point in twin_payload["damagePoints"])
    assert any(result_id in alert["detail"] for alert in screen_payload["screenAlerts"])
    assert any(
        item["resultId"] == result_id and item["references"]
        for item in knowledge_payload["knowledgeRecommendations"]
    )


def test_detection_worker_marks_batch_failed_when_asset_is_not_uploaded(client):
    presign_response = client.post(
        "/api/v1/uploads/presign",
        json={
            "filename": "IMG_NOT_UPLOADED.jpg",
            "contentType": "image/jpeg",
            "bizType": "detection-image",
        },
    )
    assert presign_response.status_code == 200
    asset_id = presign_response.json()["data"]["assetId"]

    create_response = client.post(
        "/api/v1/detection/batches",
        json={
            "siteId": "site_001",
            "componentId": "component-pillar-east",
            "assetIds": [asset_id],
            "source": "ground",
            "capturedAt": "2026-03-15T10:05:00+08:00",
        },
    )
    assert create_response.status_code == 201
    batch_id = create_response.json()["data"]["batchId"]

    import time

    time.sleep(0.4)

    read_response = client.get(f"/api/v1/detection/batches/{batch_id}")

    assert read_response.status_code == 200
    payload = read_response.json()["data"]
    assert payload["status"] == "failed"
    assert "not been uploaded" in payload["errorMessage"]
    assert any(task["status"] == "failed" for task in payload["tasks"])
    assert payload["results"] == []


def test_detection_worker_marks_batch_failed_when_asset_is_missing(client):
    create_response = client.post(
        "/api/v1/detection/batches",
        json={
            "siteId": "site_001",
            "componentId": "component-pillar-east",
            "assetIds": ["asset_missing_for_worker"],
            "source": "ground",
            "capturedAt": "2026-03-15T10:05:00+08:00",
        },
    )
    assert create_response.status_code == 201
    batch_id = create_response.json()["data"]["batchId"]

    import time

    time.sleep(0.4)

    read_response = client.get(f"/api/v1/detection/batches/{batch_id}")

    assert read_response.status_code == 200
    payload = read_response.json()["data"]
    assert payload["status"] == "failed"
    assert "does not exist" in payload["errorMessage"]
    assert payload["results"] == []


def test_local_rule_based_analyzer_uses_uploaded_file_content(client):
    first_asset_id = _create_uploaded_asset(client, "IMG_ANALYZER_A.jpg")
    second_asset_id = _create_uploaded_asset(client, "IMG_ANALYZER_B.jpg")

    first_response = client.post(
        "/api/v1/detection/batches",
        json={
            "siteId": "site_001",
            "componentId": "component-pillar-east",
            "assetIds": [first_asset_id],
            "source": "ground",
            "capturedAt": "2026-03-15T10:05:00+08:00",
        },
    )
    second_response = client.post(
        "/api/v1/detection/batches",
        json={
            "siteId": "site_001",
            "componentId": "component-pillar-east",
            "assetIds": [second_asset_id],
            "source": "ground",
            "capturedAt": "2026-03-15T10:06:00+08:00",
        },
    )
    assert first_response.status_code == 201
    assert second_response.status_code == 201

    import time

    time.sleep(0.6)

    first_payload = client.get(
        f"/api/v1/detection/batches/{first_response.json()['data']['batchId']}"
    ).json()["data"]
    second_payload = client.get(
        f"/api/v1/detection/batches/{second_response.json()['data']['batchId']}"
    ).json()["data"]

    assert first_payload["status"] == "completed"
    assert second_payload["status"] == "completed"
    assert first_payload["results"][0]["modelVersion"] == "local-rule-based-v1"
    assert second_payload["results"][0]["modelVersion"] == "local-rule-based-v1"
    assert first_payload["results"][0]["boundingBox"] != second_payload["results"][0]["boundingBox"]


def test_detection_result_review_writes_back_to_page_aggregates(client):
    asset_id = _create_uploaded_asset(client, "IMG_REVIEW_001.jpg")

    create_response = client.post(
        "/api/v1/detection/batches",
        json={
            "siteId": "site_001",
            "componentId": "component-pillar-east",
            "assetIds": [asset_id],
            "source": "ground",
            "capturedAt": "2026-03-15T10:05:00+08:00",
        },
    )

    assert create_response.status_code == 201
    batch_id = create_response.json()["data"]["batchId"]

    import time

    time.sleep(2.2)

    list_response = client.get(f"/api/v1/detection/batches/{batch_id}/results")

    assert list_response.status_code == 200
    result_items = list_response.json()["data"]["items"]
    assert len(result_items) == 3
    result_id = result_items[0]["id"]

    detail_response = client.get(f"/api/v1/detection/results/{result_id}")

    assert detail_response.status_code == 200
    assert detail_response.json()["data"]["id"] == result_id

    review_response = client.patch(
        f"/api/v1/detection/results/{result_id}/review",
        json={"reviewStatus": "approved", "note": "步骤 5 自动验收"},
    )

    assert review_response.status_code == 200
    reviewed_result = review_response.json()["data"]
    assert reviewed_result["id"] == result_id
    assert reviewed_result["reviewStatus"] == "approved"

    overview_response = client.get("/api/v1/pages/overview")
    twin_response = client.get("/api/v1/pages/twin", params={"siteId": "site_001"})
    screen_response = client.get("/api/v1/pages/screen")

    assert overview_response.status_code == 200
    assert twin_response.status_code == 200
    assert screen_response.status_code == 200

    assert any(
        result_id in event["detail"]
        for event in overview_response.json()["data"]["coordinationEvents"]
    )
    assert any(
        damage_point["id"] == result_id and damage_point["status"] == "approved"
        for damage_point in twin_response.json()["data"]["damagePoints"]
    )
    assert any(
        result_id in alert["detail"]
        for alert in screen_response.json()["data"]["screenAlerts"]
    )


def test_knowledge_recommendation_and_workorder_flow(client):
    asset_id = _create_uploaded_asset(client, "IMG_WORKORDER_001.jpg")

    create_response = client.post(
        "/api/v1/detection/batches",
        json={
            "siteId": "site_001",
            "componentId": "component-pillar-east",
            "assetIds": [asset_id],
            "source": "ground",
            "capturedAt": "2026-03-15T10:05:00+08:00",
        },
    )

    assert create_response.status_code == 201
    batch_id = create_response.json()["data"]["batchId"]

    import time

    time.sleep(2.2)

    result_items = client.get(f"/api/v1/detection/batches/{batch_id}/results").json()["data"]["items"]
    result_id = result_items[0]["id"]

    review_response = client.patch(
        f"/api/v1/detection/results/{result_id}/review",
        json={"reviewStatus": "approved", "note": "步骤 6 自动验收"},
    )

    assert review_response.status_code == 200

    recommendation_response = client.get("/api/v1/knowledge/recommendations")
    assert recommendation_response.status_code == 200
    recommendations = recommendation_response.json()["data"]["items"]
    assert any(
        item["resultId"] == result_id and item["workOrderStatus"] == "candidate" and item["references"]
        for item in recommendations
    )

    create_work_order_response = client.post(
        "/api/v1/workorders",
        json={"resultId": result_id, "note": "转正式工单"},
    )
    assert create_work_order_response.status_code == 200
    work_order_payload = create_work_order_response.json()["data"]
    assert work_order_payload["resultId"] == result_id
    assert work_order_payload["status"] == "created"

    repeated_review_response = client.patch(
        f"/api/v1/detection/results/{result_id}/review",
        json={"reviewStatus": "approved", "note": "step 6 idempotency check"},
    )
    assert repeated_review_response.status_code == 200
    repeated_work_order_response = client.get("/api/v1/workorders")
    assert repeated_work_order_response.status_code == 200
    repeated_work_orders = [
        item for item in repeated_work_order_response.json()["data"]["items"] if item["resultId"] == result_id
    ]
    assert len(repeated_work_orders) == 1
    assert repeated_work_orders[0]["status"] == "created"

    update_work_order_response = client.patch(
        f"/api/v1/workorders/{work_order_payload['workOrderId']}/status",
        json={"status": "in_progress", "note": "local status flow"},
    )
    assert update_work_order_response.status_code == 200
    assert update_work_order_response.json()["data"]["status"] == "in_progress"

    list_work_order_response = client.get("/api/v1/workorders")
    assert list_work_order_response.status_code == 200
    work_orders = list_work_order_response.json()["data"]["items"]
    assert any(item["workOrderId"] == work_order_payload["workOrderId"] for item in work_orders)

    knowledge_page_response = client.get("/api/v1/pages/knowledge")
    assert knowledge_page_response.status_code == 200
    assert any(
        item["resultId"] == result_id and item["workOrderStatus"] == "in_progress"
        for item in knowledge_page_response.json()["data"]["knowledgeRecommendations"]
    )

    screen_response = client.get("/api/v1/pages/screen")
    assert screen_response.status_code == 200
    screen_payload = screen_response.json()["data"]
    assert "病害档案驱动" in screen_payload["screenMetrics"][3]["delta"]
    assert any(event["title"].startswith("处置任务已派发") for event in screen_payload["screenEvents"])
