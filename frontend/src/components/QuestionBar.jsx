import { useState } from 'react'

function QuestionBar({ onAsk, loading }) {
  const [question, setQuestion] = useState('')

  const handleSubmit = async (event) => {
    event.preventDefault()

    const trimmedQuestion = question.trim()

    if (!trimmedQuestion || loading) {
      return
    }

    await onAsk(trimmedQuestion)
  }

  return (
    <section className="question-section">
      <div className="question-label">
        NOVA INTELLIGENCE
      </div>

      <form
        className="question-bar"
        onSubmit={handleSubmit}
      >
        <input
          type="text"
          value={question}
          onChange={(event) =>
            setQuestion(event.target.value)
          }
          placeholder="Ask NOVA a business question..."
          disabled={loading}
        />

        <button
          type="submit"
          disabled={loading}
          aria-label="Ask NOVA"
        >
          {loading ? '...' : '→'}
        </button>
      </form>
    </section>
  )
}

export default QuestionBar