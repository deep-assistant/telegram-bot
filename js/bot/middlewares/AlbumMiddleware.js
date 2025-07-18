import { createLogger } from '../../utils/logger.js';

const logger = createLogger('album_middleware');

export const AlbumMiddleware = async (ctx, next) => {
  // Store media groups for batch processing
  if (ctx.message?.media_group_id) {
    if (!ctx.session) ctx.session = {};
    if (!ctx.session.mediaGroups) ctx.session.mediaGroups = {};
    
    const groupId = ctx.message.media_group_id;
    if (!ctx.session.mediaGroups[groupId]) {
      ctx.session.mediaGroups[groupId] = [];
    }
    
    ctx.session.mediaGroups[groupId].push(ctx.message);
    logger.debug(`Added message to media group ${groupId}, total: ${ctx.session.mediaGroups[groupId].length}`);
    
    // Don't process individual messages in media groups
    return;
  }
  
  await next();
}; 