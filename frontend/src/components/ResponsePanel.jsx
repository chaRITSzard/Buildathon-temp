import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

function ResponsePanel({
  answer,
  loading,
  error,
  onDecision,
  decision,
}) {
  if (loading) {
    return (
      <section className="response-panel">
        <div className="response-status">
          NOVA IS ANALYZING...
        </div>
      </section>
    )
  }

  if (error) {
    return (
      <section className="response-panel response-error">
        <div className="response-status">
          {error}
        </div>
      </section>
    )
  }

  if (!answer) {
    return null
  }

  /*
   * Show the approval gate when NOVA is making
   * a recommendation / proposing a business action.
   *
   * Pure information questions such as:
   * "What is our ROAS?"
   * should NOT show the gate.
   */
  const question = answer.question?.toLowerCase() || ''

  const actionKeywords = [
    'should we',
    'should nova',
    'recommend',
    'recommendation',
    'increase',
    'decrease',
    'reallocate',
    'allocate',
    'shift budget',
    'scale',
    'expand',
    'pause',
    'reduce',
    'invest',
    'prioritize',
  ]

  const requiresApproval = actionKeywords.some(
    (keyword) => question.includes(keyword)
  )

  return (
    <section className="response-panel">
      <div className="response-agent">
        {answer.agent?.toUpperCase()} INTELLIGENCE
      </div>

      <div className="response-answer">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>
          {answer.answer}
        </ReactMarkdown>
      </div>

      {requiresApproval && !decision && (
        <div className="approval-gate">
          <div className="approval-label">
            ACTION REQUIRED
          </div>

          <div className="approval-title">
            Executive Approval
          </div>

          <div className="approval-description">
            NOVA has proposed a business action based on
            the available intelligence. No action will be
            executed without approval.
          </div>

          <div className="approval-actions">
            <button
              type="button"
              className="reject-button"
              onClick={() => onDecision('rejected')}
            >
              REJECT
            </button>

            <button
              type="button"
              className="approve-button"
              onClick={() => onDecision('approved')}
            >
              APPROVE ACTION →
            </button>
          </div>
        </div>
      )}

      {decision && (
        <div className={`decision-result ${decision.action}`}>
          <div className="approval-label">
            DECISION RECORDED
          </div>

          <div className="decision-message">
            {decision.action === 'approved'
              ? 'ACTION APPROVED'
              : 'ACTION REJECTED'}
          </div>
        </div>
      )}
    </section>
  )
}

export default ResponsePanel