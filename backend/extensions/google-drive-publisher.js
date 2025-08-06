const { google } = require('googleapis');
const fs = require('fs').promises;
const path = require('path');

class GoogleDrivePublisher {
    constructor(credentials) {
        this.auth = new google.auth.GoogleAuth({
            credentials: credentials,
            scopes: ['https://www.googleapis.com/auth/drive']
        });
        this.drive = google.drive({ version: 'v3', auth: this.auth });
    }

    async createCourseFolder(courseName, parentFolderId = null) {
        const folderMetadata = {
            name: courseName,
            mimeType: 'application/vnd.google-apps.folder',
            parents: parentFolderId ? [parentFolderId] : undefined
        };

        try {
            const folder = await this.drive.files.create({
                resource: folderMetadata,
                fields: 'id, name'
            });
            return folder.data;
        } catch (error) {
            throw new Error(`Failed to create course folder: ${error.message}`);
        }
    }

    async createModuleStructure(courseFolder, modules) {
        const moduleStructure = {};
        
        for (const module of modules) {
            const moduleFolder = await this.createCourseFolder(
                `Module ${module.number}: ${module.title}`,
                courseFolder.id
            );
            
            moduleStructure[module.number] = {
                folder: moduleFolder,
                lessons: {}
            };

            // Create lesson folders within each module
            for (const lesson of module.lessons) {
                const lessonFolder = await this.createCourseFolder(
                    `Lesson ${lesson.number}: ${lesson.title}`,
                    moduleFolder.id
                );
                
                moduleStructure[module.number].lessons[lesson.number] = lessonFolder;
            }
        }
        
        return moduleStructure;
    }

    async uploadContent(content, fileName, folderId, mimeType = 'text/plain') {
        const fileMetadata = {
            name: fileName,
            parents: [folderId]
        };

        const media = {
            mimeType: mimeType,
            body: content
        };

        try {
            const file = await this.drive.files.create({
                resource: fileMetadata,
                media: media,
                fields: 'id, name, webViewLink'
            });
            return file.data;
        } catch (error) {
            throw new Error(`Failed to upload content: ${error.message}`);
        }
    }

    async createGoogleDoc(title, content, folderId) {
        // Create a Google Doc
        const docMetadata = {
            name: title,
            mimeType: 'application/vnd.google-apps.document',
            parents: [folderId]
        };

        try {
            const doc = await this.drive.files.create({
                resource: docMetadata,
                fields: 'id, name, webViewLink'
            });

            // Add content to the document using Google Docs API
            const docs = google.docs({ version: 'v1', auth: this.auth });
            await docs.documents.batchUpdate({
                documentId: doc.data.id,
                resource: {
                    requests: [{
                        insertText: {
                            location: { index: 1 },
                            text: content
                        }
                    }]
                }
            });

            return doc.data;
        } catch (error) {
            throw new Error(`Failed to create Google Doc: ${error.message}`);
        }
    }

    async setPermissions(fileId, permissions) {
        for (const permission of permissions) {
            try {
                await this.drive.permissions.create({
                    fileId: fileId,
                    resource: permission
                });
            } catch (error) {
                console.error(`Failed to set permission: ${error.message}`);
            }
        }
    }

    async publishCourse(courseData) {
        try {
            // Create main course folder
            const courseFolder = await this.createCourseFolder(courseData.title);
            
            // Create module structure
            const moduleStructure = await this.createModuleStructure(
                courseFolder, 
                courseData.modules
            );

            // Upload course materials
            const uploadedFiles = {};
            
            // Upload course overview
            const overviewDoc = await this.createGoogleDoc(
                'Course Overview',
                courseData.overview,
                courseFolder.id
            );
            uploadedFiles.overview = overviewDoc;

            // Upload module content
            for (const module of courseData.modules) {
                const moduleFolder = moduleStructure[module.number];
                
                // Upload module overview
                const moduleOverview = await this.createGoogleDoc(
                    `Module ${module.number} Overview`,
                    module.overview,
                    moduleFolder.folder.id
                );

                // Upload lessons
                for (const lesson of module.lessons) {
                    const lessonFolder = moduleFolder.lessons[lesson.number];
                    
                    const lessonDoc = await this.createGoogleDoc(
                        lesson.title,
                        lesson.content,
                        lessonFolder.id
                    );

                    // Upload assessments if available
                    if (lesson.assessment) {
                        const assessmentDoc = await this.createGoogleDoc(
                            `${lesson.title} - Assessment`,
                            lesson.assessment,
                            lessonFolder.id
                        );
                    }
                }
            }

            // Set permissions for stakeholders
            const stakeholderPermissions = [
                {
                    role: 'writer',
                    type: 'user',
                    emailAddress: courseData.instructor
                },
                {
                    role: 'reader',
                    type: 'user',
                    emailAddress: courseData.reviewer
                }
            ];

            await this.setPermissions(courseFolder.id, stakeholderPermissions);

            return {
                success: true,
                courseFolder: courseFolder,
                structure: moduleStructure,
                files: uploadedFiles,
                message: `Course "${courseData.title}" successfully published to Google Drive`
            };

        } catch (error) {
            return {
                success: false,
                error: error.message,
                message: 'Failed to publish course to Google Drive'
            };
        }
    }
}

module.exports = GoogleDrivePublisher;