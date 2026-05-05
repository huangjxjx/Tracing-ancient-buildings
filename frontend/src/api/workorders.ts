import { apiRequest } from "./client";

export type WorkOrder = {
  workOrderId: string;
  resultId: string;
  batchId: string;
  siteId: string;
  componentId: string;
  title: string;
  damageTypeName: string;
  status: WorkOrderStatus;
  priority: string;
  ownerTeam: string;
  note: string;
  createdAt: string;
  updatedAt: string;
};

export type WorkOrderStatus = "candidate" | "created" | "assigned" | "in_progress" | "done";

export type WorkOrderListPayload = {
  items: WorkOrder[];
  total: number;
};

export type CreateWorkOrderRequest = {
  resultId: string;
  note?: string;
};

export type UpdateWorkOrderStatusRequest = {
  status: WorkOrderStatus;
  note?: string;
};

export function getWorkOrders() {
  return apiRequest<WorkOrderListPayload>("/api/v1/workorders");
}

export function createWorkOrder(payload: CreateWorkOrderRequest) {
  return apiRequest<WorkOrder>("/api/v1/workorders", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function updateWorkOrderStatus(workOrderId: string, payload: UpdateWorkOrderStatusRequest) {
  return apiRequest<WorkOrder>(`/api/v1/workorders/${encodeURIComponent(workOrderId)}/status`, {
    method: "PATCH",
    body: JSON.stringify(payload)
  });
}
