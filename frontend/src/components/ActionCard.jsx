function ActionCard({
  actionData,
  onApprove,
  onReject,
  loading,
}) {
  if (!actionData) {
    return null
  }

  const { action_id, action } = actionData

  const isPending =
    action.status === 'pending_approval'

  const isApproved =
    action.status === 'approved'

  const isRejected =
    action.status === 'rejected'

  return (
    <div className="action-card">

      <div className="action-card-header">
        <span className="action-label">
          ACTION PROPOSAL
        </span>

        <span
          className={`action-status ${action.status}`}
        >
          {action.status.replace('_', ' ')}
        </span>
      </div>

      <h3>{action.description}</h3>

      <div className="action-details">

        <div>
          <span>Amount</span>
          <strong>
            ₹{action.amount.toLocaleString('en-IN')}
          </strong>
        </div>

        {action.source && (
          <div>
            <span>From</span>
            <strong>{action.source}</strong>
          </div>
        )}

        {action.destination && (
          <div>
            <span>To</span>
            <strong>{action.destination}</strong>
          </div>
        )}

      </div>

      <div className="action-reason">
        <span>REASON</span>
        <p>{action.reason}</p>
      </div>

      {isPending && (
        <div className="action-controls">
          <button
            className="action-reject"
            onClick={onReject}
            disabled={loading}
          >
            REJECT
          </button>

          <button
            className="action-approve"
            onClick={onApprove}
            disabled={loading}
          >
            {loading ? 'PROCESSING...' : 'APPROVE'}
          </button>
        </div>
      )}

      {isApproved && (
        <div className="action-result approved">
          ✓ APPROVED
        </div>
      )}

      {isRejected && (
        <div className="action-result rejected">
          ACTION REJECTED
        </div>
      )}

      <small className="action-id">
        {action_id}
      </small>

    </div>
  )
}

export default ActionCard