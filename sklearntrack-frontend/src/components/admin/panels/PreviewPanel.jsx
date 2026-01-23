// PreviewPanel.jsx - Student View Preview
import React from 'react'
import ReactMarkdown from 'react-markdown'
import { Code2, Clock, Zap } from 'lucide-react'

export function PreviewPanel({ topic }) {
  return (
    <div className="p-4 h-full overflow-auto flex flex-col">
      <h2 className="text-lg font-bold text-white mb-4">Preview</h2>

      {/* METADATA */}
      <div className="mb-4 pb-4 border-b border-gray-700 space-y-2">
        <h3 className="text-base font-bold text-white truncate">{topic.title}</h3>
        <p className="text-xs text-gray-400 line-clamp-2">{topic.description}</p>
        <div className="flex flex-wrap gap-2 text-xs">
          <span className="flex items-center gap-1 text-gray-400">
            <Clock size={12} /> {topic.estimated_minutes} min
          </span>
          <span className="flex items-center gap-1 text-yellow-400">
            <Zap size={12} /> {topic.difficulty}
          </span>
        </div>
        {topic.key_concepts?.length > 0 && (
          <div className="flex flex-wrap gap-1 mt-2">
            {topic.key_concepts.slice(0, 3).map((concept, i) => (
              <span
                key={i}
                className="px-2 py-1 bg-blue-900/40 text-blue-300 rounded text-xs"
              >
                {concept}
              </span>
            ))}
            {topic.key_concepts.length > 3 && (
              <span className="px-2 py-1 bg-blue-900/40 text-blue-300 rounded text-xs">
                +{topic.key_concepts.length - 3} more
              </span>
            )}
          </div>
        )}
      </div>

      {/* CONTENT PREVIEW */}
      <div className="flex-1 prose prose-invert prose-sm max-w-none">
        <div className="text-gray-300 text-sm leading-relaxed">
          {topic.content ? (
            <ReactMarkdown
              components={{
                h1: ({ node, ...props }) => (
                  <h1 className="text-xl font-bold text-white mt-4 mb-2" {...props} />
                ),
                h2: ({ node, ...props }) => (
                  <h2 className="text-lg font-bold text-white mt-3 mb-2" {...props} />
                ),
                h3: ({ node, ...props }) => (
                  <h3 className="text-base font-semibold text-white mt-2 mb-1" {...props} />
                ),
                p: ({ node, ...props }) => (
                  <p className="mb-2 leading-relaxed" {...props} />
                ),
                ul: ({ node, ...props }) => (
                  <ul className="list-disc list-inside mb-2 space-y-1" {...props} />
                ),
                ol: ({ node, ...props }) => (
                  <ol className="list-decimal list-inside mb-2 space-y-1" {...props} />
                ),
                li: ({ node, ...props }) => (
                  <li className="mb-1" {...props} />
                ),
                code: ({ node, inline, ...props }) =>
                  inline ? (
                    <code
                      className="bg-gray-800 px-1.5 py-0.5 rounded text-yellow-300 font-mono text-xs"
                      {...props}
                    />
                  ) : (
                    <code
                      className="block bg-gray-800 p-3 rounded mb-2 overflow-x-auto text-xs font-mono text-green-300"
                      {...props}
                    />
                  ),
                blockquote: ({ node, ...props }) => (
                  <blockquote
                    className="border-l-4 border-blue-500 pl-3 italic text-blue-200 my-2"
                    {...props}
                  />
                ),
                a: ({ node, ...props }) => (
                  <a
                    className="text-blue-400 hover:text-blue-300 underline"
                    {...props}
                  />
                )
              }}
            >
              {topic.content}
            </ReactMarkdown>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <Code2 size={32} className="mx-auto mb-2 opacity-50" />
              <p>No content yet</p>
            </div>
          )}
        </div>
      </div>

      {/* FOOTER */}
      <div className="mt-4 pt-4 border-t border-gray-700 text-xs text-gray-500">
        <p>💡 This is how students will see your content</p>
      </div>
    </div>
  )
}
