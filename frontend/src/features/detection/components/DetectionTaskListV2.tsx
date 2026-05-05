import type { DetectionTask } from "../../../types/detection";

type DetectionTaskListV2Props = {
  tasks: DetectionTask[];
};

const taskStatusLabelMap: Record<DetectionTask["status"], string> = {
  pending: "等待",
  running: "执行中",
  completed: "已完成",
  failed: "失败"
};

function DetectionTaskListV2({ tasks }: DetectionTaskListV2Props) {
  return (
    <section className="panel detection-task-panel">
      <div className="panel-heading">
        <div>
          <span className="section-tag">识别任务</span>
          <h3>后台处理进度</h3>
        </div>
      </div>

      <div className="task-list">
        {tasks.map((task) => {
          const progressStyle = { width: `${task.progress}%` };

          return (
            <article className="task-card" key={task.id}>
              <div className="task-card-header">
                <div>
                  <strong>{task.title}</strong>
                  <p>{task.errorMessage ?? task.description}</p>
                </div>
                <span className={`task-status task-status-${task.status}`}>{taskStatusLabelMap[task.status]}</span>
              </div>
              <div className="task-progress-track">
                <div className="task-progress-fill" style={progressStyle} />
              </div>
              <div className="task-card-footer">
                <small>进度 {task.progress}%</small>
                <small>{task.eta}</small>
              </div>
            </article>
          );
        })}
      </div>
    </section>
  );
}

export default DetectionTaskListV2;
