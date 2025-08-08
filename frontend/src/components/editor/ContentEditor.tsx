import React, { useState } from 'react';
import { useEditor, EditorContent } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import { 
  BoldIcon, 
  ItalicIcon, 
  ListBulletIcon, 
  NumberedListIcon,
  EyeIcon,
  PencilIcon
} from '@heroicons/react/24/outline';
import { Content } from '../../types';
import { contentApi } from '../../services/api';
import toast from 'react-hot-toast';

interface ContentEditorProps {
  workflowId: string;
  content: Content[];
}

const ContentEditor: React.FC<ContentEditorProps> = ({ workflowId, content }) => {
  const [selectedContent, setSelectedContent] = useState<Content | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [isPreview, setIsPreview] = useState(false);

  const editor = useEditor({
    extensions: [StarterKit],
    content: selectedContent?.content_data?.content || '',
    editorProps: {
      attributes: {
        class: 'prose max-w-none p-4 focus:outline-none min-h-[400px]'
      }
    }
  });

  const handleSave = async () => {
    if (!selectedContent || !editor) return;

    try {
      const updatedContent = {
        ...selectedContent.content_data,
        content: editor.getHTML()
      };

      await contentApi.updateContent(workflowId, selectedContent.id, {
        content_data: updatedContent
      });

      toast.success('Content saved successfully!');
      setIsEditing(false);
    } catch (error) {
      toast.error('Failed to save content');
    }
  };

  const renderContentPreview = (item: Content) => {
    if (item.content_type === 'outline') {
      return (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold">Course Outline</h3>
          {item.content_data.modules?.map((module: any, idx: number) => (
            <div key={idx} className="border-l-4 border-primary-500 pl-4">
              <h4 className="font-medium">{module.title}</h4>
              <p className="text-sm text-gray-600">{module.description}</p>
              {module.lessons && (
                <ul className="mt-2 space-y-1">
                  {module.lessons.map((lesson: any, lessonIdx: number) => (
                    <li key={lessonIdx} className="text-sm text-gray-700">
                      • {lesson.title}
                    </li>
                  ))}
                </ul>
              )}
            </div>
          ))}
        </div>
      );
    }

    if (item.content_type === 'module') {
      return (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold">{item.content_data.title}</h3>
          <div className="prose max-w-none">
            <div dangerouslySetInnerHTML={{ __html: item.content_data.content || '' }} />
          </div>
        </div>
      );
    }

    return (
      <div className="prose max-w-none">
        <pre className="whitespace-pre-wrap text-sm">
          {JSON.stringify(item.content_data, null, 2)}
        </pre>
      </div>
    );
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[600px]">
      {/* Content List */}
      <div className="lg:col-span-1 border rounded-lg p-4 overflow-y-auto">
        <h3 className="font-semibold mb-4">Content Items</h3>
        <div className="space-y-2">
          {content.map((item) => (
            <div
              key={item.id}
              onClick={() => {
                setSelectedContent(item);
                setIsEditing(false);
                setIsPreview(false);
                if (editor) {
                  editor.commands.setContent(item.content_data?.content || '');
                }
              }}
              className={`p-3 rounded-lg cursor-pointer border transition-colors ${
                selectedContent?.id === item.id
                  ? 'border-primary-500 bg-primary-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="font-medium text-sm">
                    {item.title || item.content_type}
                  </h4>
                  <p className="text-xs text-gray-500">
                    Version {item.version}
                  </p>
                </div>
                <div className="flex items-center space-x-1">
                  {item.is_ai_generated && (
                    <span className="w-2 h-2 bg-blue-500 rounded-full" title="AI Generated" />
                  )}
                  {item.is_human_edited && (
                    <span className="w-2 h-2 bg-orange-500 rounded-full" title="Human Edited" />
                  )}
                  {item.is_approved && (
                    <span className="w-2 h-2 bg-green-500 rounded-full" title="Approved" />
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Content Editor/Preview */}
      <div className="lg:col-span-2 border rounded-lg flex flex-col">
        {selectedContent ? (
          <>
            {/* Toolbar */}
            <div className="border-b p-4 flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <h3 className="font-semibold">
                  {selectedContent.title || selectedContent.content_type}
                </h3>
                <span className="text-xs bg-gray-100 px-2 py-1 rounded">
                  v{selectedContent.version}
                </span>
              </div>
              
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => setIsPreview(!isPreview)}
                  className={`p-2 rounded ${isPreview ? 'bg-primary-100 text-primary-600' : 'text-gray-600'}`}
                >
                  <EyeIcon className="w-5 h-5" />
                </button>
                
                {selectedContent.content_type === 'module' && (
                  <button
                    onClick={() => setIsEditing(!isEditing)}
                    className={`p-2 rounded ${isEditing ? 'bg-primary-100 text-primary-600' : 'text-gray-600'}`}
                  >
                    <PencilIcon className="w-5 h-5" />
                  </button>
                )}
              </div>
            </div>

            {/* Editor Toolbar */}
            {isEditing && editor && (
              <div className="border-b p-2 flex items-center space-x-2">
                <button
                  onClick={() => editor.chain().focus().toggleBold().run()}
                  className={`p-2 rounded ${editor.isActive('bold') ? 'bg-gray-200' : ''}`}
                >
                  <BoldIcon className="w-4 h-4" />
                </button>
                <button
                  onClick={() => editor.chain().focus().toggleItalic().run()}
                  className={`p-2 rounded ${editor.isActive('italic') ? 'bg-gray-200' : ''}`}
                >
                  <ItalicIcon className="w-4 h-4" />
                </button>
                <button
                  onClick={() => editor.chain().focus().toggleBulletList().run()}
                  className={`p-2 rounded ${editor.isActive('bulletList') ? 'bg-gray-200' : ''}`}
                >
                  <ListBulletIcon className="w-4 h-4" />
                </button>
                <button
                  onClick={() => editor.chain().focus().toggleOrderedList().run()}
                  className={`p-2 rounded ${editor.isActive('orderedList') ? 'bg-gray-200' : ''}`}
                >
                  <NumberedListIcon className="w-4 h-4" />
                </button>
                
                <div className="ml-auto">
                  <button onClick={handleSave} className="btn-primary text-sm">
                    Save Changes
                  </button>
                </div>
              </div>
            )}

            {/* Content Area */}
            <div className="flex-1 overflow-y-auto">
              {isEditing && selectedContent.content_type === 'module' ? (
                <EditorContent editor={editor} />
              ) : (
                <div className="p-4">
                  {renderContentPreview(selectedContent)}
                </div>
              )}
            </div>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center text-gray-500">
            Select content to view or edit
          </div>
        )}
      </div>
    </div>
  );
};

export default ContentEditor;