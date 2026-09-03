function DecisionHistory({ decisions = [] }) {
  if (!decisions.length) {
    return (
      <section className="decision-history">
        <div className="history-header">
          DECISION HISTORY
        </div>

        <div className="history-empty">
          NO DECISIONS RECORDED
        </div>
      </section>
    )
  }

  return (
    <section className="decision-history">
      <div className="history-header">
        DECISION HISTORY
      </div>

      <div className="history-list">
        {[...decisions].reverse().map((item) => {
          const action = item.action || {}
          const status = action.status?.toLowerCase()

          return (
            <div
              key={item.action_id}
              className={`history-item ${status}`}
            >
              <div className="history-status">
                {status === 'approved' ? '✓' : '✕'}
              </div>

              <div className="history-content">
                <div className="history-decision">
                  {status?.toUpperCase()}
                </div>

                <div className="history-description">
                  {action.description ||
                    action.reason ||
                    'Business action proposed by NOVA'}
                </div>

                <div className="history-meta">
                  {action.agent
                    ? `${action.agent.toUpperCase()} AGENT`
                    : 'NOVA'}
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </section>
  )
}

export default DecisionHistory